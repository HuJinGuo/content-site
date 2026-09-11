import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const posts = defineCollection({
	loader: glob({ base: './src/content/posts', pattern: '**/*.{md,mdx}' }),
	schema: z.object({
		title: z.string(),
		description: z.string(),
		ogImage: z.string().optional(),
		series: z.string().optional(),
		episode: z.number().int().optional(),
		publishedAt: z.coerce.date(),
		// Only `published` entries are listed and get a `/posts/[slug]` page.
		status: z.enum(['draft', 'published']),
		episodeTotal: z.number().int().optional(),
		nextTitle: z.string().optional(),
		nextHook: z.string().optional(),
		// Unpublished follow-ups stay `#` — never point at relative .md paths outside the site.
		nextHref: z.string().optional(),
	}),
});

export const collections = { posts };
