// @ts-check
import { defineConfig } from 'astro/config';

// Static HTML output only. No server endpoints or adapters.
export default defineConfig({
	output: 'static',
});
