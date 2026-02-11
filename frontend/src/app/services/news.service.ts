/**
 * News service – handles all HTTP communication with the Django REST backend.
 *
 * Features:
 * - Fetches paginated articles with filtering support
 * - Retrieves categories and sources for filter dropdowns
 * - Handles errors gracefully with RxJS
 */

import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, of } from 'rxjs';

import { Article, Category, PaginatedResponse, Source } from '../models/news.model';

@Injectable({
  providedIn: 'root',
})
export class NewsService {
  private readonly baseUrl = 'http://localhost:8000/api/news';

  constructor(private http: HttpClient) {}

  /**
   * Get a paginated list of articles.
   * @param page     Page number (1-indexed)
   * @param category Category slug to filter by
   * @param source   Source ID to filter by
   * @param country  Country code to filter by
   * @param search   Search keyword
   */
  getArticles(
    page: number = 1,
    category?: string,
    source?: string,
    country?: string,
    search?: string,
  ): Observable<PaginatedResponse<Article>> {
    let params = new HttpParams().set('page', page.toString());

    if (category) params = params.set('category', category);
    if (source) params = params.set('source', source);
    if (country) params = params.set('country', country);
    if (search) params = params.set('search', search);

    const url = `${this.baseUrl}/articles/`;
    console.log('Fetching articles from:', url, 'with params:', params.toString());

    return this.http.get<PaginatedResponse<Article>>(url, { params }).pipe(
      catchError((error) => {
        console.error('Error fetching articles:', error);
        return of({ count: 0, next: null, previous: null, results: [] });
      }),
    );
  }

  /**
   * Get all available categories.
   */
  getCategories(): Observable<Category[]> {
    const url = `${this.baseUrl}/categories/`;
    console.log('Fetching categories from:', url);
    return this.http.get<Category[]>(url).pipe(
      catchError((error) => {
        console.error('Error fetching categories:', error);
        return of([]);
      }),
    );
  }

  /**
   * Get all available sources.
   */
  getSources(): Observable<Source[]> {
    const url = `${this.baseUrl}/sources/`;
    console.log('Fetching sources from:', url);
    return this.http.get<Source[]>(url).pipe(
      catchError((error) => {
        console.error('Error fetching sources:', error);
        return of([]);
      }),
    );
  }

  /**
   * Trigger a manual news fetch on the backend.
   */
  fetchNews(category?: string, country?: string, query?: string): Observable<{ message: string }> {
    return this.http
      .post<{ message: string }>(`${this.baseUrl}/fetch/`, {
        category,
        country,
        query,
      })
      .pipe(
        catchError((error) => {
          console.error('Error triggering fetch:', error);
          return of({ message: 'Failed to fetch news.' });
        }),
      );
  }
}
