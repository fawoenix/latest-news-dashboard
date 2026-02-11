import { Component, Input } from '@angular/core';
import { DatePipe } from '@angular/common';
import { Article } from '../../models/news.model';

/**
 * ArticleCardComponent displays a single news article as a card.
 * Clicking the card opens the article in a new browser tab.
 */
@Component({
  selector: 'app-article-card',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './article-card.component.html',
})
export class ArticleCardComponent {
  @Input({ required: true }) article!: Article;

  /** Fallback image when url_to_image is missing or fails to load */
  readonly fallbackImage =
    'https://images.unsplash.com/photo-1504711434969-e33886168d5c?w=800&q=80';

  /**
   * Open the original article URL in a new tab.
   */
  openArticle(): void {
    window.open(this.article.url, '_blank', 'noopener,noreferrer');
  }

  /**
   * Handle image load errors by replacing with fallback.
   */
  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = this.fallbackImage;
  }
}
