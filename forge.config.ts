import type { ForgeConfig } from '@electron-forge/shared-types';
import { MakerSquirrel } from '@electron-forge/maker-squirrel';
import { MakerZIP } from '@electron-forge/maker-zip';
import { MakerDeb } from '@electron-forge/maker-deb';
import { MakerRpm } from '@electron-forge/maker-rpm';
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
      /python[\/\\]data[\/\\]shared/,
      /python[\/\\]data[\/\\]visualizaciones/,
      /python[\/\\]data[\/\\]\.backups/,
      /python[\/\\]venv/,
      /python[\/\\]__pycache__/,
      /python[\/\\]config[\/\\]__pycache__/,
      /python[\/\\]core[\/\\]__pycache__/,
      /python[\/\\]core[\/\\]visualizaciones[\/\\]__pycache__/,
      /__pycache__/,
      /\.pyc$/,
    ],
    // Windows-specific icon (create this file if needed)
    icon: './resources/icons/icon',
    // App metadata
    appCopyright: 'Copyright © 2024 AI Tourism Opinion Analyzer',
    win32metadata: {
      CompanyName: 'AI Tourism Analyzer',
      ProductName: 'AI Tourism Opinion Analyzer',
      FileDescription: 'AI-powered tourism review analysis tool',
    },
  },
  rebuildConfig: {},
  makers: [
    new MakerSquirrel({
      // Windows installer configuration
      name: 'AITourismAnalyzer',
      authors: 'victorwkey',
      description: 'AI-powered tourism review analysis tool',
      // Uncomment and set path when you have an icon
      // iconUrl: 'https://url/to/icon.ico',
      // setupIcon: './resources/icons/icon.ico',
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
};

export default config;
