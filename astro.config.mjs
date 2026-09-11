// @ts-check
import { defineConfig } from 'astro/config';

// Static HTML output only. T0 has no server endpoints or adapters.
export default defineConfig({
	output: 'static',
});
