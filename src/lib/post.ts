export type NextTeaser = {
	title: string;
	hook: string;
};

export type ActionBlock = {
	heading: string;
	hint?: string;
	content: string;
};

export type SplitPost = {
	main: string;
	action: ActionBlock | null;
	teaser: NextTeaser | null;
};

function stripEditorialMeta(body: string): string {
	return body
		.replace(/^(?:>\s*)?发布状态[：:][^\n]*(?:\n(?!\n|## )[^\n]*)*\n*/u, '')
		.replace(/^>\s*发布状态[：:][\s\S]*?(?:\n{2,}|$)/u, '')
		.trimStart();
}

function extractTeaser(body: string): { text: string; teaser: NextTeaser | null } {
	const match = body.match(/\n(?:---\s*\n+)?\*\*下篇预告[：:]\*\*\s*([\s\S]+?)\s*$/u);
	if (!match) return { text: body, teaser: null };

	const rest = match[1].trim();
	const parts = rest.split(/——|—{1,2}|-{2,}/u);
	const title = (parts[0] ?? '').trim();
	const hook = parts.slice(1).join('').trim();

	return {
		text: body.slice(0, match.index).replace(/\n---\s*$/u, '').trimEnd(),
		teaser: title ? { title, hook } : null,
	};
}

function extractAction(body: string): { text: string; action: ActionBlock | null } {
	const match = body.match(/\n## 今天就做([^\n]*)\n([\s\S]*?)\s*(?=\n## |\n---\s*$|$)/u);
	if (!match || match.index == null) return { text: body, action: null };

	const suffix = match[1].trim();
	const hint = suffix.replace(/^[（(]/u, '').replace(/[）)]$/u, '').trim() || undefined;

	return {
		text: `${body.slice(0, match.index)}\n${body.slice(match.index + match[0].length)}`,
		action: {
			heading: '今天就做',
			hint,
			content: match[2].trim(),
		},
	};
}

/** Pull 「今天就做」 and 下篇预告 out of the article body. */
export function splitPostBody(body: string): SplitPost {
	let text = stripEditorialMeta(body);
	const teaserResult = extractTeaser(text);
	text = teaserResult.text;
	const actionResult = extractAction(text);
	text = actionResult.text.replace(/\n---\s*$/u, '').trim();

	return {
		main: text,
		action: actionResult.action,
		teaser: teaserResult.teaser,
	};
}
