export const SITE_NAME = '内容发布站';
export const SERIES_HOME_HREF = '/';
/** Default episode count for the 大学生 AI 上手 series badge. */
export const DEFAULT_SERIES_TOTAL = 8;

export function padEpisode(n: number): string {
	return String(n).padStart(2, '0');
}

export function seriesBadge(
	series: string | undefined,
	episode: number | undefined,
	total = DEFAULT_SERIES_TOTAL,
): string | undefined {
	if (!series) return undefined;
	if (episode == null) return series;
	return `${series} · ${padEpisode(episode)}/${padEpisode(total)}`;
}

export function isExternalHref(href: string): boolean {
	return /^https?:\/\//i.test(href);
}
