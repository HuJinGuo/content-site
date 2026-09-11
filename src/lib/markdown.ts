import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { markdownToHtml } from 'satteri';

const DO_TODAY_HEADING = /^## (今天就做[^\n]*)/m;

export function splitDoToday(markdown: string): {
	body: string;
	actionTitle: string | null;
	actionMarkdown: string | null;
} {
	const match = markdown.match(DO_TODAY_HEADING);
	if (!match || match.index === undefined) {
		return { body: markdown.trim(), actionTitle: null, actionMarkdown: null };
	}

	const actionTitle = match[1].trim();
	const afterHeading = markdown.slice(match.index + match[0].length);
	const nextHeading = afterHeading.search(/^## /m);
	const actionMarkdown = (nextHeading === -1 ? afterHeading : afterHeading.slice(0, nextHeading)).trim();
	const before = markdown.slice(0, match.index).trim();
	const after = nextHeading === -1 ? '' : afterHeading.slice(nextHeading).trim();
	const body = [before, after]
		.filter(Boolean)
		.join('\n\n')
		.replace(/(?:\n|^)---\s*$/u, '')
		.trim();
	return { body, actionTitle, actionMarkdown: actionMarkdown || null };
}

function escapeHtml(value: string): string {
	return value
		.replaceAll('&', '&amp;')
		.replaceAll('<', '&lt;')
		.replaceAll('>', '&gt;')
		.replaceAll('"', '&quot;');
}

function enhanceHtml(html: string): string {
	html = html.replace(/<a\s+([^>]*?)>/gi, (full, attrs: string) => {
		const href = attrs.match(/\bhref="([^"]+)"/i)?.[1] ?? '';
		const external = /^(https?:)?\/\//i.test(href);
		if (!external || /\btarget=/i.test(attrs)) return full;
		return `<a ${attrs.trim()} target="_blank" rel="noopener noreferrer">`;
	});

	html = html.replace(/<table\b/gi, '<div class="table-scroll"><table').replace(/<\/table>/gi, '</table></div>');

	html = html.replace(/<img\b([^>]*)>/gi, (full, attrs: string) => {
		const src = attrs.match(/\bsrc="([^"]+)"/i)?.[1] ?? '';
		const alt = attrs.match(/\balt="([^"]*)"/i)?.[1] ?? '';
		const local = src.startsWith('/') && !src.startsWith('//');
		if (local) {
			const filePath = join(process.cwd(), 'public', src.split('?')[0] ?? src);
			if (!existsSync(filePath)) {
				const label = alt || '图片暂缺';
				return `<div class="img-placeholder" role="img" aria-label="${escapeHtml(label)}">${escapeHtml(label)}</div>`;
			}
		}
		if (/\bonerror=/i.test(attrs)) return full;
		return `<img${attrs} onerror="window.__imgPh&&window.__imgPh(this)">`;
	});

	html = html.replace(/<p>\s*(<div class="img-placeholder"[\s\S]*?<\/div>)\s*<\/p>/g, '$1');

	return html;
}

export function renderMarkdown(markdown: string): string {
	const { html } = markdownToHtml(markdown, {
		features: { gfm: true, smartPunctuation: true },
	});
	return enhanceHtml(html);
}
