import type { ForgeConfig } from '@electron-forge/shared-types';
import { MakerSquirrel } from '@electron-forge/maker-squirrel';
import { MakerZIP } from '@electron-forge/maker-zip';
import { MakerDeb } from '@electron-forge/maker-deb';
import { MakerRpm } from '@electron-forge/maker-rpm';
import { PublisherGithub } from '@electron-forge/publisher-github';
import { VitePlugin } from '@electron-forge/plugin-vite';
import { FusesPlugin } from '@electron-forge/plugin-fuses';
import { FuseV1Options, FuseVersion } from '@electron/fuses';

const config: ForgeConfig = {
  packagerConfig: {
    asar: true,
    // Include Python directory in the package
    extraResource: ['./python'],
    // Exclude runtime-generated artifacts from the packaged app
    ignore: [
      /python[/\\]data[/\\]shared/,
      /python[/\\]data[/\\]visualizaciones/,
      /python[/\\]data[/\\]\.backups/,
      /python[/\\]venv/,
      /python[/\\]__pycache__/,
      /python[/\\]config[/\\]__pycache__/,
      /python[/\\]core[/\\]__pycache__/,
      /python[/\\]core[/\\]visualizaciones[/\\]__pycache__/,
      /__pycache__/,
      /\.pyc$/,
    ],
    // Windows-specific icon (create this file if needed)
    icon: './resources/icons/icon',
    // App metadata
    appCopyright: 'Copyright © 2025-2026 TourlyAI',
    win32metadata: {
      CompanyName: 'TourlyAI',
      ProductName: 'TourlyAI',
      FileDescription: 'AI-powered review analysis tool',
    },
  },
  rebuildConfig: {},
  makers: [
    new MakerSquirrel({
      // Windows installer configuration
      name: 'TourlyAI',
      authors: 'victorwkey',
      description: 'AI-powered review analysis tool',
      setupIcon: './resources/icons/icon.ico',
      // Icon shown in Windows "Add/Remove Programs" list.
      // Squirrel.Windows writes this URL to the registry (DisplayIcon).
      // Using the repo's raw icon URL so it works without a local file path at install time.
      iconUrl: 'https://raw.githubusercontent.com/victorwkey/AI-Tourism-Opinion-Analyzer/main/resources/icons/icon.ico',
      // Code signing — set these environment variables in CI or locally:
      //   WINDOWS_CERTIFICATE_FILE: path to .pfx file
      //   WINDOWS_CERTIFICATE_PASSWORD: certificate password
      ...(process.env.WINDOWS_CERTIFICATE_FILE ? {
        certificateFile: process.env.WINDOWS_CERTIFICATE_FILE,
        certificatePassword: process.env.WINDOWS_CERTIFICATE_PASSWORD,
      } : {}),
    }),
    new MakerZIP({}, ['darwin', 'win32']),
    new MakerRpm({}),
    new MakerDeb({}),
  ],
  plugins: [
    new VitePlugin({
      // `build` can specify multiple entry builds, which can be Main process, Preload scripts, Worker process, etc.
      // If you are familiar with Vite configuration, it will look really familiar.
      build: [
        {
          // `entry` is just an alias for `build.lib.entry` in the corresponding file of `config`.
          entry: 'src/main.ts',
          config: 'vite.main.config.ts',
          target: 'main',
        },
        {
          entry: 'src/preload.ts',
          config: 'vite.preload.config.ts',
          target: 'preload',
        },
      ],
      renderer: [
        {
          name: 'main_window',
          config: 'vite.renderer.config.ts',
        },
      ],
    }),
    // Fuses are used to enable/disable various Electron functionality
    // at package time, before code signing the application
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
  publishers: [
    new PublisherGithub({
      repository: {
        owner: 'victorwkey',
        name: 'AI-Tourism-Opinion-Analyzer',
      },
      prerelease: false,
      draft: true, // Creates a draft release so you can review before publishing
    }),
  ],
};

export default config;
