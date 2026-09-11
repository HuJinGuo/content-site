import { defineHastPlugin, markdownToHtml } from 'satteri';

const prosePlugin = defineHastPlugin({
	name: 'prose-enhance',
	element: [
		{
			filter: ['a'],
			visit(node, ctx) {
				const href = node.properties?.href;
				if (typeof href === 'string' && /^https?:\/\//i.test(href)) {
					ctx.setProperty(node, 'target', '_blank');
					ctx.setProperty(node, 'rel', 'noopener noreferrer');
				}
			},
		},
		{
			filter: ['table'],
			visit(node, ctx) {
				ctx.wrapNode(node, { raw: '<div class="table-scroll"></div>' });
			},
		},
		{
			filter: ['img'],
			visit(node, ctx) {
				const existing = node.properties?.className;
				const classes = Array.isArray(existing)
					? existing.map(String)
					: typeof existing === 'string'
						? existing.split(/\s+/)
						: [];
				if (!classes.includes('md-img')) classes.push('md-img');
				ctx.setProperty(node, 'className', classes);
				ctx.setProperty(node, 'loading', 'lazy');
				ctx.setProperty(node, 'decoding', 'async');
			},
		},
	],
});

export async function renderMarkdown(source: string): Promise<string> {
	const result = await Promise.resolve(
		markdownToHtml(source, {
			features: { gfm: true },
			hastPlugins: [prosePlugin],
		}),
	);
	return result.html;
}
