export const SITE_NAME = '内容发布站';

/** Known series length. Used for the `系列 · 01/08` badge when frontmatter omits episodeTotal. */
export const SERIES_EPISODE_TOTAL: Record<string, number> = {
	'大学生 AI 上手': 8,
};

export function seriesBadge(data: {
	series?: string;
	episode?: number;
	episodeTotal?: number;
}): string | null {
	if (!data.series) return null;
	if (data.episode == null) return data.series;
	const total = data.episodeTotal ?? SERIES_EPISODE_TOTAL[data.series];
	if (total) {
		return `${data.series} · ${String(data.episode).padStart(2, '0')}/${String(total).padStart(2, '0')}`;
	}
	return `${data.series} · ${data.episode}`;
}
