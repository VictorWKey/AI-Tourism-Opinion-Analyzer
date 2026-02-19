/// <reference types="@electron-forge/plugin-vite/forge-vite-env" />

declare const __APP_VERSION__: string;

declare module '*.png' {
  const src: string;
  export default src;
}

declare module '*.svg' {
  const src: string;
  export default src;
}

declare module '*.jpg' {
  const src: string;
  export default src;
}
