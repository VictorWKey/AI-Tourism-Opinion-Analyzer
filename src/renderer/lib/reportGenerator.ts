/**
 * PDF Report Generator
 * =====================
 * Generates a professional PDF report using jsPDF.
 * Reads analysis data from the filesystem and composes
 * the document according to the user's ReportConfig.
 */

import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { ReportConfig, VisualizationCategory } from './reportTypes';
import { formatDuration } from './utils';

/** Safely get the Y position after the last autoTable call */
function getLastAutoTableY(doc: jsPDF, fallback: number): number {
  const d = doc as unknown as { lastAutoTable?: { finalY?: number } };
  return d.lastAutoTable?.finalY ?? fallback;
}

/* ──────────────── Colour palette ──────────────── */
const COLORS = {
  primary: [37, 99, 235] as [number, number, number],      // blue-600
  primaryLight: [219, 234, 254] as [number, number, number], // blue-100
  dark: [15, 23, 42] as [number, number, number],            // slate-900
  text: [51, 65, 85] as [number, number, number],            // slate-700
  muted: [100, 116, 139] as [number, number, number],        // slate-500
  light: [241, 245, 249] as [number, number, number],        // slate-100
  white: [255, 255, 255] as [number, number, number],
  green: [34, 197, 94] as [number, number, number],
  red: [239, 68, 68] as [number, number, number],
  amber: [245, 158, 11] as [number, number, number],
  gray: [148, 163, 184] as [number, number, number],
  purple: [168, 85, 247] as [number, number, number],
};

/* ──────────────── Data types (mirror Metrics.tsx) ──────────────── */

interface InsightsKpis {
  total_opiniones: number;
  porcentaje_positivo: number;
  porcentaje_neutro: number;
  porcentaje_negativo: number;
  calificacion_promedio: number;
  mejor_categoria: string;
  peor_categoria: string;
  subtopico_mas_mencionado: string;
}

interface FortalezaItem {
  categoria: string;
  subtopico?: string;
  porcentaje_positivo: number;
  total_menciones: number;
}

interface DebilidadItem {
  categoria: string;
  subtopico?: string;
  porcentaje_negativo: number;
  total_menciones: number;
}

interface DistributionItem {
  cantidad: number;
  porcentaje: number;
}

interface TopicItem {
  nombre: string;
  cantidad: number;
  porcentaje: number;
}

interface EstadisticasDataset {
  total_registros: number;
  sentimiento: Record<string, DistributionItem> | null;
  subjetividad: Record<string, DistributionItem> | null;
  calificacion: Record<string, DistributionItem> | null;
  calificacion_promedio?: number;
  calificacion_mediana?: number;
  categorias: Record<string, DistributionItem> | null;
  categorias_meta?: {
    total_asignaciones: number;
    promedio_categorias_por_review: number;
    categorias_unicas: number;
  };
  topicos: TopicItem[] | null;
  temporal: {
    fecha_min: string;
    fecha_max: string;
    rango_dias: number;
    registros_con_fecha: number;
    registros_sin_fecha: number;
  } | null;
  longitud_texto: {
    promedio: number;
    mediana: number;
    minimo: number;
    maximo: number;
  } | null;
}

interface InsightsData {
  fecha_generacion: string;
  validacion_dataset: {
    total_opiniones: number;
    tiene_fechas: boolean;
    rango_temporal_dias: number;
    categorias_identificadas: number;
    tiene_topicos: boolean;
    subtopicos_detectados: number;
    sentimientos: { positivo: number; neutro: number; negativo: number };
    recomendaciones: string[];
  };
  kpis: InsightsKpis;
  fortalezas: FortalezaItem[];
  debilidades: DebilidadItem[];
  resumenes: {
    estructurado?: {
      global?: string;
      por_categoria?: Record<string, string>;
    };
  };
  estadisticas_dataset?: EstadisticasDataset;
}

interface StrategicInsightsData {
  metadata: { fecha_generacion: string; total_reviews: number };
  insights: { global: string };
}

interface GenerationReport {
  fecha_generacion: string;
  dataset: {
    total_opiniones: number;
    tiene_fechas: boolean;
    tiene_calificacion: boolean;
    rango_temporal_dias: number;
    categorias_identificadas: number;
    cobertura_topicos: boolean;
  };
  visualizaciones: {
    total_generadas: number;
    total_omitidas: number;
    por_seccion: Record<string, number>;
    lista_generadas: string[];
  };
  omitidas: string[];
  recomendaciones: string[];
}

interface TimingRecord {
  phase: number;
  name: string;
  duration: number;
  status: string;
  startTime?: string;
  endTime?: string;
}

interface ImageInfo {
  id: string;
  name: string;
  path: string;
  category: string;
  categoryLabel: string;
}

/* ──────────────── Translation helper ──────────────── */
type TFunc = (key: string, options?: Record<string, unknown>) => string;

/** Clean quotes from Python strings */
const clean = (v: string | number): string => {
  if (typeof v === 'string') return v.replace(/^["']|["']$/g, '');
  return String(v);
};

/** Translate category names */
const tCat = (cat: string, t: TFunc): string => {
  const cleaned = clean(cat);
  const key = `common:dataLabels.categories.${cleaned}`;
  const translated = t(key);
  return translated !== key ? translated : cleaned;
};

/** Translate sentiment labels */
const tSent = (label: string, t: TFunc): string => {
  const key = `common:dataLabels.sentiment.${label}`;
  const translated = t(key);
  return translated !== key ? translated : label;
};

/** Translate subjectivity labels */
const tSubj = (label: string, t: TFunc): string => {
  const key = `common:dataLabels.subjectivity.${label}`;
  const translated = t(key);
  return translated !== key ? translated : label;
};

/* ──────────────── PDF Builder ──────────────── */

export interface GenerateReportOptions {
  config: ReportConfig;
  t: TFunc;
  datasetName: string;
  outputDir: string;
  timingRecords: TimingRecord[];
  /** Optional custom file name (without extension). If omitted, a timestamped name is used. */
  customFileName?: string;
}

/**
 * Main report generation function.
 * Returns the file path of the generated PDF.
 */
export async function generatePdfReport(options: GenerateReportOptions): Promise<string> {
  const { config, t, datasetName, outputDir, timingRecords, customFileName } = options;

  // 1. Load data
  const pythonDataDir = await window.electronAPI.app.getPythonDataDir();

  const insightsRaw = await window.electronAPI.files.readFile(
    `${pythonDataDir}/visualizaciones/insights_textuales.json`
  );
  const insightsData: InsightsData | null =
    insightsRaw.success && insightsRaw.content ? JSON.parse(insightsRaw.content) : null;

  let strategicData: StrategicInsightsData | null = null;
  if (config.sections.strategicInsights) {
    const raw = await window.electronAPI.files.readFile(
      `${pythonDataDir}/shared/insights_estrategicos.json`
    );
    strategicData = raw.success && raw.content ? JSON.parse(raw.content) : null;
  }

  let generationReportData: GenerationReport | null = null;
  if (config.sections.generationReport) {
    const raw = await window.electronAPI.files.readFile(
      `${pythonDataDir}/visualizaciones/reporte_generacion.json`
    );
    generationReportData = raw.success && raw.content ? JSON.parse(raw.content) : null;
  }

  // Load visualization images if needed
  let images: ImageInfo[] = [];
  if (config.sections.visualizations) {
    // Determine theme - use light for PDF (better for printing)
    const chartsPath = `${pythonDataDir}/visualizaciones/light`;
    const chartsExist = await window.electronAPI.files.exists(chartsPath);
    const actualPath = chartsExist ? chartsPath : `${pythonDataDir}/visualizaciones/dark`;
    const imagesResult = await window.electronAPI.files.listImages(actualPath);
    if (imagesResult.success && imagesResult.images) {
      images = imagesResult.images;
    }
  }

  // 2. Create PDF
  const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const margin = 20;
  const contentW = pageW - 2 * margin;
  let y = margin;

  // Track sections for TOC
  const tocEntries: { title: string; page: number }[] = [];

  /* ── Helper: manage page breaks ── */
  const footerMargin = 6; // space reserved for the footer text
  const ensureSpace = (needed: number) => {
    if (y + needed > pageH - margin - footerMargin) {
      doc.addPage();
      y = margin;
    }
  };

  /* ── Helper: add footer ── */
  const addFooter = (pageNum: number) => {
    doc.setFontSize(8);
    doc.setTextColor(...COLORS.muted);
    doc.text(t('reports:pdf.footerText'), pageW / 2, pageH - 8, { align: 'center' });
    if (config.includePageNumbers) {
      doc.text(String(pageNum), pageW - margin, pageH - 8, { align: 'right' });
    }
  };

  /* ── Helper: section heading ── */
  const addSectionHeading = (title: string) => {
    ensureSpace(20);
    // Add a colored bar
    doc.setFillColor(...COLORS.primary);
    doc.rect(margin, y, contentW, 0.8, 'F');
    y += 5;
    doc.setFontSize(16);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.dark);
    doc.text(title, margin, y + 5);
    y += 14;
    tocEntries.push({ title, page: doc.getNumberOfPages() });
  };

  /* ── Helper: draw a simple colored bar (sentiment/progress) ── */
  const drawBar = (x: number, yPos: number, width: number, height: number, segments: { pct: number; color: [number, number, number] }[]) => {
    let currentX = x;
    for (const seg of segments) {
      const segWidth = (seg.pct / 100) * width;
      if (segWidth > 0) {
        doc.setFillColor(...seg.color);
        doc.roundedRect(currentX, yPos, segWidth, height, 1, 1, 'F');
        currentX += segWidth;
      }
    }
  };

  /* ── Helper: wrap long text into PDF lines ── */
  const addWrappedText = (text: string, x: number, yStart: number, maxWidth: number, fontSize: number, color: [number, number, number] = COLORS.text, fontStyle = 'normal'): number => {
    doc.setFontSize(fontSize);
    doc.setFont('helvetica', fontStyle);
    doc.setTextColor(...color);
    const lines = doc.splitTextToSize(text, maxWidth);
    const lineHeight = fontSize * 0.45;
    let currentY = yStart;
    for (const line of lines) {
      y = currentY;                // sync global y so ensureSpace checks the real position
      ensureSpace(lineHeight + 2);
      currentY = y;               // if page break happened, currentY jumps to new page top
      doc.text(line, x, currentY);
      currentY += lineHeight;
    }
    return currentY;
  };

  /* ═══════════════════════════════════════════
     COVER PAGE
     ═══════════════════════════════════════════ */
  if (config.sections.coverPage) {
    // Background accent
    doc.setFillColor(...COLORS.primary);
    doc.rect(0, 0, pageW, 100, 'F');

    // Title
    doc.setFontSize(28);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.white);
    const titleLines = doc.splitTextToSize(config.title || t('reports:pdf.coverTitle'), contentW);
    let titleY = 40;
    for (const line of titleLines) {
      doc.text(line, pageW / 2, titleY, { align: 'center' });
      titleY += 12;
    }

    // Subtitle
    doc.setFontSize(14);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(219, 234, 254);
    doc.text(t('reports:pdf.coverSubtitle'), pageW / 2, titleY + 4, { align: 'center' });

    // Info box
    y = 120;
    doc.setFillColor(...COLORS.light);
    doc.roundedRect(margin + 20, y, contentW - 40, 60, 3, 3, 'F');

    const infoX = margin + 30;
    y += 15;
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...COLORS.muted);

    if (config.includeDate) {
      doc.text(t('reports:pdf.generatedOn'), infoX, y);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.dark);
      doc.text(new Date().toLocaleDateString(), infoX + 60, y);
      y += 10;
    }

    if (config.includeDatasetInfo) {
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...COLORS.muted);
      doc.text(t('reports:pdf.dataset'), infoX, y);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.dark);
      doc.text(datasetName || '—', infoX + 60, y);
      y += 10;

      if (insightsData) {
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...COLORS.muted);
        doc.text(t('reports:pdf.totalReviews'), infoX, y);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...COLORS.dark);
        doc.text(String(insightsData.kpis.total_opiniones), infoX + 60, y);
        y += 10;

        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...COLORS.muted);
        doc.text(t('reports:pdf.analysisDate'), infoX, y);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...COLORS.dark);
        doc.text(new Date(insightsData.fecha_generacion).toLocaleDateString(), infoX + 60, y);
      }
    }

    addFooter(1);
    doc.addPage();
    y = margin;
  }

  /* ═══════════════════════════════════════════
     TABLE OF CONTENTS (placeholder – filled later)
     ═══════════════════════════════════════════ */
  const tocPageNum = config.sections.tableOfContents ? doc.getNumberOfPages() : -1;
  if (config.sections.tableOfContents) {
    // Reserve a TOC page – we'll write it after we know all entries
    doc.addPage();
    y = margin;
  }

  /* ═══════════════════════════════════════════
     KPIs
     ═══════════════════════════════════════════ */
  if (config.sections.kpis && insightsData) {
    addSectionHeading(t('reports:pdf.kpisTitle'));
    const kpis = insightsData.kpis;
    const stats = insightsData.estadisticas_dataset;

    const kpiItems: { label: string; value: string }[] = [
      { label: t('reports:pdf.totalReviews'), value: String(kpis.total_opiniones) },
      { label: t('reports:pdf.avgRating'), value: `${kpis.calificacion_promedio}/5` },
      { label: t('reports:pdf.positivePercent'), value: `${kpis.porcentaje_positivo}%` },
      { label: t('reports:pdf.neutralPercent'), value: `${kpis.porcentaje_neutro}%` },
      { label: t('reports:pdf.negativePercent'), value: `${kpis.porcentaje_negativo}%` },
      { label: t('reports:pdf.bestCategory'), value: tCat(kpis.mejor_categoria, t) },
      { label: t('reports:pdf.opportunityArea'), value: tCat(kpis.peor_categoria, t) },
      { label: t('reports:pdf.mainSubtopic'), value: clean(kpis.subtopico_mas_mencionado) },
    ];

    if (stats?.categorias_meta) {
      kpiItems.push({
        label: t('reports:pdf.catsPerReview'),
        value: String(stats.categorias_meta.promedio_categorias_por_review.toFixed(1)),
      });
    }
    if (stats?.longitud_texto) {
      kpiItems.push({
        label: t('reports:pdf.avgTextLength'),
        value: `${Math.round(stats.longitud_texto.promedio)} ${t('reports:pdf.characters')}`,
      });
    }

    // Draw KPI grid (2 columns)
    const colW = (contentW - 6) / 2;
    for (let i = 0; i < kpiItems.length; i += 2) {
      ensureSpace(16);
      for (let j = 0; j < 2 && i + j < kpiItems.length; j++) {
        const item = kpiItems[i + j];
        const xOff = margin + j * (colW + 6);
        doc.setFillColor(...COLORS.light);
        doc.roundedRect(xOff, y, colW, 13, 2, 2, 'F');
        doc.setFontSize(8);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...COLORS.muted);
        doc.text(item.label, xOff + 4, y + 5);
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...COLORS.dark);
        doc.text(item.value, xOff + 4, y + 11);
      }
      y += 16;
    }

    // Sentiment bar
    ensureSpace(16);
    y += 3;
    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.dark);
    doc.text(t('reports:pdf.sentimentTitle'), margin, y);
    y += 5;
    drawBar(margin, y, contentW, 5, [
      { pct: kpis.porcentaje_positivo, color: COLORS.green },
      { pct: kpis.porcentaje_neutro, color: COLORS.gray },
      { pct: kpis.porcentaje_negativo, color: COLORS.red },
    ]);
    y += 8;
    doc.setFontSize(7);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...COLORS.green);
    doc.text(`${t('reports:pdf.positivePercent')} ${kpis.porcentaje_positivo}%`, margin, y);
    doc.setTextColor(...COLORS.gray);
    doc.text(`${t('reports:pdf.neutralPercent')} ${kpis.porcentaje_neutro}%`, margin + 55, y);
    doc.setTextColor(...COLORS.red);
    doc.text(`${t('reports:pdf.negativePercent')} ${kpis.porcentaje_negativo}%`, margin + 110, y);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     SENTIMENT DISTRIBUTION TABLE
     ═══════════════════════════════════════════ */
  if (config.sections.sentimentAnalysis && insightsData?.estadisticas_dataset?.sentimiento) {
    addSectionHeading(t('reports:pdf.sentimentTitle'));
    const sent = insightsData.estadisticas_dataset.sentimiento;
    const body = Object.entries(sent).map(([label, v]) => [
      tSent(label, t),
      String(v.cantidad),
      `${v.porcentaje}%`,
    ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.sentiment'), t('reports:pdf.count'), t('reports:pdf.percentage')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.primary, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: COLORS.light },
    });
    y = getLastAutoTableY(doc, y + 30);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     SUBJECTIVITY DISTRIBUTION TABLE
     ═══════════════════════════════════════════ */
  if (config.sections.subjectivityAnalysis && insightsData?.estadisticas_dataset?.subjetividad) {
    addSectionHeading(t('reports:pdf.subjectivityTitle'));
    const subj = insightsData.estadisticas_dataset.subjetividad;
    const body = Object.entries(subj).map(([label, v]) => [
      tSubj(label, t),
      String(v.cantidad),
      `${v.porcentaje}%`,
    ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.type'), t('reports:pdf.count'), t('reports:pdf.percentage')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.purple, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: COLORS.light },
    });
    y = getLastAutoTableY(doc, y + 30);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     RATING DISTRIBUTION TABLE
     ═══════════════════════════════════════════ */
  if (config.sections.ratingDistribution && insightsData?.estadisticas_dataset?.calificacion) {
    addSectionHeading(t('reports:pdf.ratingTitle'));
    const cal = insightsData.estadisticas_dataset.calificacion;
    const body = Object.entries(cal).map(([stars, v]) => [
      `${'★'.repeat(Number(stars))} (${stars})`,
      String(v.cantidad),
      `${v.porcentaje}%`,
    ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.stars'), t('reports:pdf.count'), t('reports:pdf.percentage')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.amber, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: COLORS.light },
    });
    y = getLastAutoTableY(doc, y + 30);
    const calStats = insightsData.estadisticas_dataset;
    if (calStats?.calificacion_promedio != null) {
      ensureSpace(6);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'italic');
      doc.setTextColor(...COLORS.muted);
      doc.text(
        t('reports:pdf.avgRatingNote', { avg: calStats.calificacion_promedio, median: calStats.calificacion_mediana ?? '-' }),
        margin, y,
      );
      y += 5;
    }
    y += 8;
  }

  /* ═══════════════════════════════════════════
     CATEGORY DISTRIBUTION TABLE
     ═══════════════════════════════════════════ */
  if (config.sections.categoryAnalysis && insightsData?.estadisticas_dataset?.categorias) {
    addSectionHeading(t('reports:pdf.categoryTitle'));
    const cats = insightsData.estadisticas_dataset.categorias;
    const body = Object.entries(cats)
      .sort((a, b) => b[1].cantidad - a[1].cantidad)
      .map(([cat, v]) => [
        tCat(cat, t),
        String(v.cantidad),
        `${v.porcentaje}%`,
      ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.category'), t('reports:pdf.reviews'), t('reports:pdf.percentage')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.primary, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: COLORS.light },
    });
    y = getLastAutoTableY(doc, y + 30);
    const catMeta = insightsData.estadisticas_dataset?.categorias_meta;
    if (catMeta) {
      ensureSpace(6);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'italic');
      doc.setTextColor(...COLORS.muted);
      doc.text(
        t('reports:pdf.categoryMetaNote', { n: catMeta.categorias_unicas, total: catMeta.total_asignaciones, avg: catMeta.promedio_categorias_por_review.toFixed(1) }),
        margin, y,
      );
      y += 5;
    }
    y += 8;
  }

  /* ═══════════════════════════════════════════
     TOPIC / SUB-THEME ANALYSIS
     ═══════════════════════════════════════════ */
  if (config.sections.topicAnalysis && insightsData?.estadisticas_dataset?.topicos?.length) {
    addSectionHeading(t('reports:pdf.topicTitle'));
    const body = insightsData.estadisticas_dataset.topicos.map((tp, idx) => [
      String(idx + 1),
      clean(tp.nombre),
      String(tp.cantidad),
      `${tp.porcentaje}%`,
    ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.rank'), t('reports:pdf.subtopic'), t('reports:pdf.mentions'), t('reports:pdf.percentage')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.primary, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: COLORS.light },
    });
    y = getLastAutoTableY(doc, y + 30);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     TEMPORAL ANALYSIS
     ═══════════════════════════════════════════ */
  if (config.sections.temporalAnalysis && insightsData?.estadisticas_dataset?.temporal) {
    addSectionHeading(t('reports:pdf.temporalTitle'));
    const temp = insightsData.estadisticas_dataset.temporal;
    const body = [
      [t('reports:pdf.oldestDate'), temp.fecha_min],
      [t('reports:pdf.newestDate'), temp.fecha_max],
      [t('reports:pdf.timeRange'), `${temp.rango_dias} ${t('reports:pdf.days')}`],
      [t('reports:pdf.reviewsWithDate'), String(temp.registros_con_fecha)],
      [t('reports:pdf.reviewsWithoutDate'), String(temp.registros_sin_fecha)],
    ];
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      body,
      theme: 'plain',
      bodyStyles: { fontSize: 10, textColor: COLORS.text },
      columnStyles: {
        0: { fontStyle: 'bold', cellWidth: 60 },
      },
    });
    y = getLastAutoTableY(doc, y + 30);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     DATASET VALIDATION
     ═══════════════════════════════════════════ */
  if (config.sections.datasetValidation && insightsData?.validacion_dataset) {
    addSectionHeading(t('reports:pdf.datasetValidationTitle'));
    const val = insightsData.validacion_dataset;
    const valBody: string[][] = [
      [t('reports:pdf.datesAvailable'), val.tiene_fechas ? `${t('reports:pdf.yes')} (${val.rango_temporal_dias} ${t('reports:pdf.days')})` : t('reports:pdf.no')],
      [t('reports:pdf.categoriesIdentified'), String(val.categorias_identificadas)],
      [t('reports:pdf.subtopicsDetected'), val.tiene_topicos ? String(val.subtopicos_detectados) : t('reports:pdf.no')],
    ];
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      body: valBody,
      theme: 'plain',
      bodyStyles: { fontSize: 10, textColor: COLORS.text },
      columnStyles: { 0: { fontStyle: 'bold', cellWidth: 70 } },
    });
    y = getLastAutoTableY(doc, y + 30);
    if (val.recomendaciones.length > 0) {
      ensureSpace(10);
      doc.setFontSize(9);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.dark);
      doc.text(t('reports:pdf.validationRecommendations'), margin, y);
      y += 5;
      for (const rec of val.recomendaciones) {
        y = addWrappedText(`• ${rec}`, margin + 2, y, contentW - 2, 8, COLORS.muted);
        y += 2;
      }
    }
    y += 8;
  }

  /* ═══════════════════════════════════════════
     GENERATION REPORT
     ═══════════════════════════════════════════ */
  if (config.sections.generationReport && generationReportData) {
    addSectionHeading(t('reports:pdf.generationReportTitle'));
    const gr = generationReportData;

    // Summary row: total generated / omitted
    const grBody: string[][] = [
      [t('reports:pdf.totalGenerated'), String(gr.visualizaciones.total_generadas)],
      [t('reports:pdf.totalOmitted'), String(gr.visualizaciones.total_omitidas)],
    ];
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      body: grBody,
      theme: 'plain',
      bodyStyles: { fontSize: 10, textColor: COLORS.text },
      columnStyles: { 0: { fontStyle: 'bold', cellWidth: 70 } },
    });
    y = getLastAutoTableY(doc, y + 20);
    y += 4;

    // By-section breakdown
    if (Object.keys(gr.visualizaciones.por_seccion).length > 0) {
      ensureSpace(22);
      doc.setFontSize(9);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.dark);
      doc.text(t('reports:pdf.bySectionHeading'), margin, y);
      y += 4;
      const secBody = Object.entries(gr.visualizaciones.por_seccion).map(([sec, cnt]) => [
        sec.replace(/_/g, ' '),
        String(cnt),
      ]);
      autoTable(doc, {
        startY: y,
        margin: { left: margin, right: margin },
        head: [[t('reports:pdf.section'), t('reports:pdf.chartsCount')]],
        body: secBody,
        theme: 'striped',
        headStyles: { fillColor: COLORS.primary, fontSize: 9 },
        bodyStyles: { fontSize: 9, textColor: COLORS.text },
        alternateRowStyles: { fillColor: COLORS.light },
      });
      y = getLastAutoTableY(doc, y + 30);
      y += 4;
    }

    // Omitted visualizations
    if (gr.omitidas.length > 0) {
      ensureSpace(10);
      doc.setFontSize(9);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.amber);
      doc.text(t('reports:pdf.omittedList'), margin, y);
      y += 5;
      for (const item of gr.omitidas) {
        y = addWrappedText(`• ${item}`, margin + 2, y, contentW - 2, 8, COLORS.muted);
        y += 2;
      }
    }

    // Recommendations
    if (gr.recomendaciones.length > 0) {
      ensureSpace(10);
      doc.setFontSize(9);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.dark);
      doc.text(t('reports:pdf.validationRecommendations'), margin, y);
      y += 5;
      for (const rec of gr.recomendaciones) {
        y = addWrappedText(`• ${rec}`, margin + 2, y, contentW - 2, 8, COLORS.muted);
        y += 2;
      }
    }
    y += 8;
  }

  /* ═══════════════════════════════════════════
     STRENGTHS
     ═══════════════════════════════════════════ */
  if (config.sections.strengths && insightsData?.fortalezas?.length) {
    addSectionHeading(t('reports:pdf.strengthsTitle'));
    const body = insightsData.fortalezas.slice(0, 8).map((f, idx) => [
      String(idx + 1),
      tCat(f.categoria, t),
      f.subtopico || '—',
      `${f.porcentaje_positivo.toFixed(1)}%`,
      String(f.total_menciones),
    ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.rank'), t('reports:pdf.category'), t('reports:pdf.subtopic'), t('reports:pdf.positivePercentLabel'), t('reports:pdf.mentions')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.green, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: [240, 253, 244] },
    });
    y = getLastAutoTableY(doc, y + 30);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     OPPORTUNITIES
     ═══════════════════════════════════════════ */
  if (config.sections.opportunities && insightsData?.debilidades?.length) {
    addSectionHeading(t('reports:pdf.opportunitiesTitle'));
    const body = insightsData.debilidades.slice(0, 8).map((d, idx) => [
      String(idx + 1),
      tCat(d.categoria, t),
      d.subtopico || '—',
      `${d.porcentaje_negativo.toFixed(1)}%`,
      String(d.total_menciones),
    ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.rank'), t('reports:pdf.category'), t('reports:pdf.subtopic'), t('reports:pdf.negativePercentLabel'), t('reports:pdf.mentions')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.red, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: [254, 242, 242] },
    });
    y = getLastAutoTableY(doc, y + 30);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     VISUALIZATIONS (chart images) — Smart Grid Layout
     ═══════════════════════════════════════════ */
  if (config.sections.visualizations && images.length > 0) {
    addSectionHeading(t('reports:pdf.visualizationsTitle'));

    // Filter by enabled categories
    const enabledCats = Object.entries(config.visualizationCategories)
      .filter(([, enabled]) => enabled)
      .map(([cat]) => cat as VisualizationCategory);

    // Map category key → folder prefix & i18n label key
    const categoryFolderMap: Record<VisualizationCategory, string> = {
      sentimientos: '01_sentimientos',
      subjetividad: '02_subjetividad',
      categorias: '03_categorias',
      topicos: '04_topicos',
      temporal: '05_temporal',
      texto: '06_texto',
      combinados: '07_combinados',
    };

    const categoryOrder: VisualizationCategory[] = [
      'sentimientos', 'subjetividad', 'categorias',
      'topicos', 'temporal', 'texto', 'combinados',
    ];

    const filteredImages = images.filter((img) => {
      return enabledCats.some((cat) => {
        const folder = categoryFolderMap[cat];
        return img.category === folder || img.path.includes(folder);
      });
    });

    // Increased limit for better coverage
    const MAX_IMAGES = 25;
    const imagesToInclude = filteredImages.slice(0, MAX_IMAGES);

    if (filteredImages.length > MAX_IMAGES) {
      console.warn(`[ReportGen] Limiting to ${MAX_IMAGES} images (${filteredImages.length} available)`);
    }

    // ── Pre-load all images & compute dimensions ──
    interface PreparedImage {
      dataUrl: string;
      name: string;
      category: string;
      aspectRatio: number;   // width / height
      widthPx: number;
      heightPx: number;
    }

    const preparedImages: PreparedImage[] = [];
    for (const img of imagesToInclude) {
      try {
        const result = await window.electronAPI.files.readImageBase64(img.path);
        if (result.success && result.dataUrl) {
          const compressedDataUrl = await compressImage(result.dataUrl, 0.75);
          const dims = await getImageDimensions(compressedDataUrl);
          preparedImages.push({
            dataUrl: compressedDataUrl,
            name: img.name,
            category: img.category || '',
            aspectRatio: dims.width / dims.height,
            widthPx: dims.width,
            heightPx: dims.height,
          });
        }
      } catch (err) {
        console.warn('[ReportGen] Failed to load image:', img.name, err);
      }
    }

    // ── Group images by category, preserving order ──
    const imagesByCategory = new Map<string, PreparedImage[]>();
    for (const cat of categoryOrder) {
      const folder = categoryFolderMap[cat];
      const catImages = preparedImages.filter(
        (img) => img.category === folder || img.category.includes(folder) || img.name.includes(folder),
      );
      if (catImages.length > 0) {
        imagesByCategory.set(cat, catImages);
      }
    }
    // Catch any uncategorized images
    const categorized = new Set(preparedImages.filter((img) =>
      categoryOrder.some((cat) => {
        const folder = categoryFolderMap[cat];
        return img.category === folder || img.category.includes(folder) || img.name.includes(folder);
      }),
    ));
    const uncategorized = preparedImages.filter((img) => !categorized.has(img));
    if (uncategorized.length > 0) {
      const existing = imagesByCategory.get('combinados') || [];
      imagesByCategory.set('combinados', [...existing, ...uncategorized]);
    }

    // ── Layout constants ──
    const GAP = 6;                          // gap between side-by-side charts (mm)
    const CHART_PADDING = 3;                // padding inside chart frame (mm)
    const LABEL_HEIGHT = 6;                 // space for chart label below frame
    const halfW = (contentW - GAP) / 2;     // width of each column in 2-col layout
    const WIDE_THRESHOLD = 1.2;             // aspect ratio above which chart is "landscape" → can go side-by-side
    const TALL_THRESHOLD = 0.85;            // aspect ratio below which chart is "portrait" → full width

    /** Draw a single chart in a framed card */
    const drawChartCard = (
      pImg: PreparedImage,
      x: number,
      yStart: number,
      availableW: number,
    ): number => {
      // Compute image size in mm within the available card width
      const innerW = availableW - 2 * CHART_PADDING;
      const maxH = pageH - 2 * margin - 30; // max chart height
      const rawH = innerW / pImg.aspectRatio;
      const imgHmm = Math.min(rawH, maxH);
      const imgWmm = imgHmm * pImg.aspectRatio;
      const finalImgW = Math.min(imgWmm, innerW);
      const finalImgH = finalImgW / pImg.aspectRatio;

      const cardH = finalImgH + 2 * CHART_PADDING + LABEL_HEIGHT;

      // Card background
      doc.setFillColor(248, 250, 252);       // slate-50
      doc.setDrawColor(226, 232, 240);        // slate-200
      doc.roundedRect(x, yStart, availableW, cardH, 2, 2, 'FD');

      // Image centered within the card
      const imgX = x + CHART_PADDING + (innerW - finalImgW) / 2;
      const imgY = yStart + CHART_PADDING;
      doc.addImage(pImg.dataUrl, 'JPEG', imgX, imgY, finalImgW, finalImgH);

      // Label below the image
      doc.setFontSize(7);
      doc.setFont('helvetica', 'italic');
      doc.setTextColor(...COLORS.muted);
      const displayName = pImg.name.replace(/\.(png|jpg|svg|webp)$/i, '').replace(/_/g, ' ');
      const truncatedName = displayName.length > 60 ? displayName.slice(0, 57) + '...' : displayName;
      doc.text(truncatedName, x + availableW / 2, yStart + cardH - 2, { align: 'center' });

      return cardH;
    };

    // ── Render each category group ──
    for (const [catKey, catImages] of imagesByCategory) {
      // Category sub-heading
      ensureSpace(22);
      const catLabel = t(`reports:visualizationCategories.${catKey}`);

      doc.setFillColor(239, 246, 255);        // blue-50
      doc.setDrawColor(191, 219, 254);         // blue-200
      doc.roundedRect(margin, y, contentW, 9, 1.5, 1.5, 'FD');
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.primary);
      doc.text(catLabel, margin + 4, y + 6.2);
      y += 13;

      // Separate images into landscape-ish (can pair) and portrait/tall (full width)
      const queue = [...catImages];
      let i = 0;
      while (i < queue.length) {
        const img1 = queue[i];
        const isLandscape1 = img1.aspectRatio >= TALL_THRESHOLD;

        // Try to pair two landscape charts side-by-side
        if (isLandscape1 && i + 1 < queue.length) {
          const img2 = queue[i + 1];
          const isLandscape2 = img2.aspectRatio >= TALL_THRESHOLD;

          if (isLandscape2) {
            // ── 2-column layout ──
            const h1 = (halfW - 2 * CHART_PADDING) / img1.aspectRatio + 2 * CHART_PADDING + LABEL_HEIGHT;
            const h2 = (halfW - 2 * CHART_PADDING) / img2.aspectRatio + 2 * CHART_PADDING + LABEL_HEIGHT;
            const rowH = Math.max(h1, h2);
            ensureSpace(rowH + 4);

            drawChartCard(img1, margin, y, halfW);
            drawChartCard(img2, margin + halfW + GAP, y, halfW);
            y += rowH + 4;
            i += 2;
            continue;
          }
        }

        // ── Single full-width chart ──
        const fullH = (contentW - 2 * CHART_PADDING) / img1.aspectRatio + 2 * CHART_PADDING + LABEL_HEIGHT;
        ensureSpace(fullH + 4);
        drawChartCard(img1, margin, y, contentW);
        y += fullH + 4;
        i += 1;
      }

      y += 2; // Extra spacing after category group
    }

    // Add note if images were omitted
    if (filteredImages.length > MAX_IMAGES) {
      ensureSpace(10);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'italic');
      doc.setTextColor(...COLORS.muted);
      doc.text(
        `Note: ${filteredImages.length - MAX_IMAGES} additional visualizations omitted to maintain PDF file size`,
        pageW / 2,
        y,
        { align: 'center' },
      );
      y += 10;
    }
  }

  /* ═══════════════════════════════════════════
     STRUCTURED SUMMARIES
     ═══════════════════════════════════════════ */
  if (config.sections.summaries && insightsData?.resumenes?.estructurado) {
    addSectionHeading(t('reports:pdf.summariesTitle'));
    const summaries = insightsData.resumenes.estructurado;

    if (config.summaryOptions.global && summaries.global) {
      ensureSpace(15);
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...COLORS.primary);
      doc.text(t('reports:pdf.globalSummary'), margin, y);
      y += 7;
      y = addWrappedText(stripMarkdown(summaries.global), margin, y, contentW, 9);
      y += 6;
    }

    if (config.summaryOptions.categories && summaries.por_categoria) {
      const categories = Object.entries(summaries.por_categoria);
      const selectedCats = config.summaryOptions.selectedCategories;

      for (const [catName, content] of categories) {
        // If specific categories selected, filter
        if (selectedCats.length > 0 && !selectedCats.includes(catName)) continue;

        ensureSpace(15);
        doc.setFontSize(11);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...COLORS.primary);
        doc.text(t('reports:pdf.categorySummary', { category: tCat(catName, t) }), margin, y);
        y += 6;
        y = addWrappedText(stripMarkdown(content), margin, y, contentW, 9);
        y += 6;
      }
    }
  }

  /* ═══════════════════════════════════════════
     STRATEGIC INSIGHTS
     ═══════════════════════════════════════════ */
  if (config.sections.strategicInsights && strategicData) {
    addSectionHeading(t('reports:pdf.insightsTitle'));
    y = addWrappedText(stripMarkdown(strategicData.insights.global), margin, y, contentW, 9);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     PIPELINE TIMING
     ═══════════════════════════════════════════ */
  if (config.sections.pipelineTiming && timingRecords.length > 0) {
    addSectionHeading(t('reports:pdf.timingTitle'));
    const body = timingRecords.map((rec) => [
      String(rec.phase),
      t(`common:phases.${rec.phase}.name`),
      formatDuration(rec.duration),
      rec.status === 'completed' ? t('reports:pdf.completed') : t('reports:pdf.failed'),
    ]);
    const totalDuration = timingRecords.reduce((sum, r) => sum + (r.duration || 0), 0);
    body.push([
      '',
      t('reports:pdf.totalTime'),
      formatDuration(totalDuration),
      '',
    ]);
    autoTable(doc, {
      startY: y,
      margin: { left: margin, right: margin },
      head: [[t('reports:pdf.rank'), t('reports:pdf.phase'), t('reports:pdf.duration'), t('reports:pdf.status')]],
      body,
      theme: 'striped',
      headStyles: { fillColor: COLORS.primary, fontSize: 9 },
      bodyStyles: { fontSize: 9, textColor: COLORS.text },
      alternateRowStyles: { fillColor: COLORS.light },
    });
    y = getLastAutoTableY(doc, y + 30);
    y += 8;
  }

  /* ═══════════════════════════════════════════
     ADD FOOTERS TO ALL PAGES
     ═══════════════════════════════════════════ */
  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    addFooter(i);
  }

  /* ═══════════════════════════════════════════
     FILL TABLE OF CONTENTS (now we know pages)
     ═══════════════════════════════════════════ */
  if (config.sections.tableOfContents && tocPageNum > 0) {
    doc.setPage(tocPageNum);
    let tocY = margin;

    doc.setFillColor(...COLORS.primary);
    doc.rect(margin, tocY, contentW, 0.8, 'F');
    tocY += 7;
    doc.setFontSize(18);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...COLORS.dark);
    doc.text(t('reports:pdf.tableOfContents'), margin, tocY + 5);
    tocY += 16;

    doc.setFontSize(10);
    for (const entry of tocEntries) {
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...COLORS.text);
      doc.text(entry.title, margin, tocY);
      doc.setTextColor(...COLORS.muted);
      doc.text(`${t('reports:pdf.page')} ${entry.page}`, pageW - margin, tocY, { align: 'right' });
      // Dotted line
      const titleWidth = doc.getTextWidth(entry.title);
      const pageNumWidth = doc.getTextWidth(`${t('reports:pdf.page')} ${entry.page}`);
      const dotsStart = margin + titleWidth + 3;
      const dotsEnd = pageW - margin - pageNumWidth - 3;
      if (dotsEnd > dotsStart) {
        doc.setTextColor(...COLORS.muted);
        const dots = '.'.repeat(Math.max(0, Math.floor((dotsEnd - dotsStart) / 1.5)));
        doc.text(dots, dotsStart, tocY);
      }
      tocY += 7;
    }
  }

  /* ═══════════════════════════════════════════
     SAVE TO FILE
     ═══════════════════════════════════════════ */
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const sanitized = customFileName
    ? customFileName.replace(/[<>:"/\\|?*]/g, '_').trim()
    : '';
  const fileName = sanitized ? `${sanitized}.pdf` : `report_${timestamp}.pdf`;
  const filePath = `${outputDir}/${fileName}`;

  // Get PDF as ArrayBuffer and convert to Uint8Array for IPC transfer
  // Uint8Array serializes properly through Electron's structured clone
  const pdfArrayBuffer = doc.output('arraybuffer');
  const pdfData = new Uint8Array(pdfArrayBuffer);

  // Write the PDF data via IPC (no base64 conversion needed)
  const writeResult = await window.electronAPI.files.writeArrayBuffer(
    filePath,
    pdfData,
  );

  if (writeResult.success) {
    return filePath;
  } else {
    throw new Error(writeResult.error || 'Failed to write PDF');
  }
}

/* ──────────────── Utility functions ──────────────── */

/** Compress an image data URL to reduce file size */
function compressImage(dataUrl: string, quality: number = 0.7): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      // Limit maximum dimensions to reduce file size while keeping charts crisp
      const maxDimension = 1600;
      let width = img.width;
      let height = img.height;
      
      if (width > maxDimension || height > maxDimension) {
        if (width > height) {
          height = (height / width) * maxDimension;
          width = maxDimension;
        } else {
          width = (width / height) * maxDimension;
          height = maxDimension;
        }
      }
      
      canvas.width = width;
      canvas.height = height;
      
      if (ctx) {
        ctx.drawImage(img, 0, 0, width, height);
        // Convert to JPEG with quality compression
        resolve(canvas.toDataURL('image/jpeg', quality));
      } else {
        resolve(dataUrl); // Fallback to original if canvas fails
      }
    };
    img.onerror = () => resolve(dataUrl); // Fallback on error
    img.src = dataUrl;
  });
}

/** Simple markdown stripper for PDF text */
function stripMarkdown(text: string): string {
  return text
    .replace(/#{1,6}\s+/g, '')        // headings
    .replace(/\*\*(.+?)\*\*/g, '$1')  // bold
    .replace(/\*(.+?)\*/g, '$1')      // italic
    .replace(/__(.+?)__/g, '$1')      // bold
    .replace(/_(.+?)_/g, '$1')        // italic
    .replace(/`(.+?)`/g, '$1')        // code
    .replace(/~~(.+?)~~/g, '$1')      // strikethrough
    .replace(/\[(.+?)\]\(.+?\)/g, '$1') // links
    .replace(/^[-*+]\s+/gm, '• ')     // list items
    .replace(/^\d+\.\s+/gm, '')       // numbered lists
    .replace(/^>\s+/gm, '')           // blockquotes
    .replace(/^---+$/gm, '')          // horizontal rules
    .replace(/[\u{1F300}-\u{1F9FF}\u{2600}-\u{27BF}\u{FE00}-\u{FE0F}\u{1FA00}-\u{1FA9F}\u{1FA70}-\u{1FAFF}\u{2702}-\u{27B0}\u{200D}\u{20E3}\u{E0020}-\u{E007F}\u{2300}-\u{23FF}\u{2B50}\u{2B55}\u{2934}\u{2935}\u{25AA}\u{25AB}\u{25FB}-\u{25FE}\u{2B1B}\u{2B1C}\u{26A0}\u{2705}\u{274C}\u{274E}\u{2611}\u{2612}\u{2328}\u{23CF}\u{23E9}-\u{23F3}\u{23F8}-\u{23FA}\u{FE0F}]/gu, '')  // emojis
    .replace(/\n{3,}/g, '\n\n')       // excessive newlines
    .trim();
}

/** Get image dimensions from a data URL */
function getImageDimensions(dataUrl: string): Promise<{ width: number; height: number }> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve({ width: img.naturalWidth, height: img.naturalHeight });
    img.onerror = () => resolve({ width: 800, height: 600 }); // fallback
    img.src = dataUrl;
  });
}
