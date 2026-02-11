import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { NewsService } from '../../services/news.service';
import { Article, Category, Source } from '../../models/news.model';
import { ArticleCardComponent } from '../article-card/article-card.component';

/**
 * DashboardComponent is the main page of the application.
 *
 * Features:
 * - Displays news articles in a responsive card grid
 * - Search bar for full-text search
 * - Filter dropdowns for category and source
 * - Pagination with 50 articles per page
 */
@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, ArticleCardComponent],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  // Data
  articles: Article[] = [];
  categories: Category[] = [];
  sources: Source[] = [];

  // Filters
  searchQuery = '';
  selectedCategory = '';
  selectedSource = '';

  // Pagination
  currentPage = 1;
  totalCount = 0;
  pageSize = 50;
  totalPages = 0;

  // UI state
  loading = false;
  error = '';

  constructor(
    private newsService: NewsService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadSources();
    this.loadArticles();
  }

  /**
   * Load articles with current filters and pagination.
   */
  loadArticles(): void {
    this.loading = true;
    this.error = '';

    console.log('Loading articles...', {
      page: this.currentPage,
      category: this.selectedCategory,
      source: this.selectedSource,
      search: this.searchQuery,
    });

    this.newsService
      .getArticles(
        this.currentPage,
        this.selectedCategory || undefined,
        this.selectedSource || undefined,
        undefined,
        this.searchQuery || undefined,
      )
      .subscribe({
        next: (response) => {
          console.log('Articles loaded:', response);
          console.log('Results count:', response?.results?.length);
          console.log('Total count:', response?.count);
          this.articles = response.results || [];
          this.totalCount = response.count || 0;
          this.totalPages = Math.ceil(this.totalCount / this.pageSize);
          this.loading = false;
          console.log('Loading complete, articles:', this.articles.length);
          this.cdr.markForCheck(); // Force change detection
        },
        error: (err) => {
          console.error('Error loading articles:', err);
          this.error = 'Failed to load articles. Please try again.';
          this.loading = false;
          this.cdr.markForCheck();
        },
      });
  }

  /**
   * Load all categories for the filter dropdown.
   */
  loadCategories(): void {
    console.log('Loading categories...');
    this.newsService.getCategories().subscribe({
      next: (categories) => {
        console.log('Categories loaded:', categories.length);
        this.categories = categories;
      },
      error: (err) => {
        console.error('Error loading categories:', err);
      },
    });
  }

  /**
   * Load all sources for the filter dropdown.
   */
  loadSources(): void {
    console.log('Loading sources...');
    this.newsService.getSources().subscribe({
      next: (sources) => {
        console.log('Sources loaded:', sources.length);
        this.sources = sources;
      },
      error: (err) => {
        console.error('Error loading sources:', err);
      },
    });
  }

  /**
   * Handle search form submission.
   */
  onSearch(): void {
    this.currentPage = 1;
    this.loadArticles();
  }

  /**
   * Handle filter changes – reset to page 1 and reload.
   */
  onFilterChange(): void {
    this.currentPage = 1;
    this.loadArticles();
  }

  /**
   * Clear all filters and search.
   */
  clearFilters(): void {
    this.searchQuery = '';
    this.selectedCategory = '';
    this.selectedSource = '';
    this.currentPage = 1;
    this.loadArticles();
  }

  /**
   * Navigate to a specific page.
   */
  goToPage(page: number): void {
    if (page < 1 || page > this.totalPages) return;
    this.currentPage = page;
    this.loadArticles();
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /**
   * Generate page numbers for pagination controls.
   * Shows a window of pages around the current page.
   */
  getPageNumbers(): number[] {
    const pages: number[] = [];
    const maxVisible = 5;
    let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
    const end = Math.min(this.totalPages, start + maxVisible - 1);

    // Adjust start if we're near the end
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }

  /**
   * Check if any filters are currently active.
   */
  hasActiveFilters(): boolean {
    return !!(this.searchQuery || this.selectedCategory || this.selectedSource);
  }

  /**
   * TrackBy function for article list to improve performance
   */
  trackByArticleId(index: number, article: Article): number {
    return article.id;
  }
}
