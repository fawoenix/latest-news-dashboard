/**
 * Article model interface matching the Django REST API response.
 */
export interface Article {
  id: number;
  source_name: string;
  category_name: string | null;
  author: string;
  title: string;
  description: string;
  url: string;
  url_to_image: string;
  published_at: string;
  content?: string;
  country: string;
}

/**
 * Category model interface.
 */
export interface Category {
  id: number;
  name: string;
  slug: string;
  article_count: number;
}

/**
 * Source model interface.
 */
export interface Source {
  id: number;
  source_id: string;
  name: string;
  description: string;
  url: string;
  country: string;
  language: string;
  article_count: number;
}

/**
 * Paginated response from the Django REST API.
 */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
