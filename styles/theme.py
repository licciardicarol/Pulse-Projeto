"""Tokens de design da landing page do Pulse."""

from typing import Final


class Theme:
    """Constantes visuais compartilhadas entre as telas do Pulse."""

    COLORS: Final[dict[str, str]] = {
        "background": "#0B1220",
        "background_secondary": "#111B2E",
        "background_tertiary": "#0A2347",
        "primary": "#2B8CFF",
        "primary_hover": "#4A9DFF",
        "primary_soft": "rgba(43, 140, 255, 0.12)",
        "surface": "#111B2E",
        "surface_hover": "#172746",
        "border": "rgba(255, 255, 255, 0.08)",
        "border_strong": "rgba(59, 147, 255, 0.28)",
        "text_primary": "#FFFFFF",
        "text_secondary": "#9FB0C8",
        "text_muted": "#6F829A",
        "success": "#34D399",
        "warning": "#FBBF24",
        "hero_start": "#0B1220",
        "hero_middle": "#0A2347",
        "hero_end": "#00378A",
    }

    FONT_FAMILIES: Final[str] = (
        "'Plus Jakarta Sans', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
    )

    SPACING: Final[dict[str, str]] = {
        "section_y": "88px",
        "section_x": "24px",
        "card_padding": "24px",
        "container": "1200px",
    }

    RADIUS: Final[dict[str, str]] = {
        "sm": "10px",
        "md": "14px",
        "lg": "18px",
        "xl": "24px",
        "pill": "999px",
    }

    SHADOWS: Final[dict[str, str]] = {
        "card": "0 18px 45px rgba(0, 0, 0, 0.25)",
        "card_hover": "0 24px 60px rgba(43, 140, 255, 0.12)",
        "focus": "0 0 0 3px rgba(43, 140, 255, 0.35)",
    }

    TRANSITIONS: Final[dict[str, str]] = {
        "fast": "150ms ease",
        "slow": "200ms ease",
    }


THEME = Theme()

LANDING_PAGE_CSS: Final[str] = """
html { scroll-behavior: smooth; }
body { background: #0B1220; }

.landing-page {
  color: #FFFFFF;
  background: #0B1220;
  font-family: 'Plus Jakarta Sans', 'Segoe UI', sans-serif;
}

.landing-page * { box-sizing: border-box; }

.landing-nav {
  position: sticky;
  top: 0;
  z-index: 40;
  background: rgba(11, 18, 32, 0.72);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  transition: background 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
}

.landing-nav.is-scrolled {
  background: rgba(11, 18, 32, 0.92);
  border-bottom-color: rgba(59, 147, 255, 0.22);
  box-shadow: 0 10px 35px rgba(0, 0, 0, 0.2);
}

.landing-button,
.landing-button-secondary,
.landing-link,
.landing-cta-link {
  transition: transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease, background 200ms ease;
}

.landing-button:active,
.landing-button-secondary:active,
.landing-cta-link:active {
  transform: scale(0.97);
}

.landing-button:hover,
.landing-button-secondary:hover,
.landing-cta-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(43, 140, 255, 0.16);
}

.landing-button:focus-visible,
.landing-button-secondary:focus-visible,
.landing-cta-link:focus-visible,
.landing-nav-link:focus-visible,
.landing-feature-card:focus-visible,
.landing-faq-item:focus-visible {
  outline: 3px solid rgba(43, 140, 255, 0.35);
  outline-offset: 3px;
}

.landing-button-secondary {
  background: #0B1220;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  color: #FFFFFF;
  min-height: 44px;
}

.landing-button-secondary:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.landing-button,
.landing-button-secondary,
.landing-nav-link {
  min-height: 44px;
}

.landing-hero {
  background: linear-gradient(135deg, #0B1220 0%, #0A2347 55%, #00378A 100%);
  position: relative;
  overflow: hidden;
}

.landing-hero::before {
  content: "";
  position: absolute;
  inset: -20% -10% auto auto;
  width: 32rem;
  height: 32rem;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(59, 147, 255, 0.18), transparent 68%);
  filter: blur(18px);
  animation: pulse-glow 10s ease-in-out infinite alternate;
}

.landing-feature-card,
.landing-audience-item,
.landing-faq-item {
  transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
}

.landing-feature-card:hover,
.landing-audience-item:hover,
.landing-faq-item:hover {
  transform: translateY(-4px);
  border-color: rgba(59, 147, 255, 0.35);
  box-shadow: 0 18px 45px rgba(43, 140, 255, 0.08);
}

.landing-feature-card:hover .landing-icon,
.landing-audience-item:hover .landing-icon {
  transform: scale(1.08);
}

.landing-section,
.landing-cta,
.landing-footer {
  text-align: center;
}

.landing-faq-section > div {
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.landing-faq {
  text-align: left;
}

.landing-faq-header {
  cursor: pointer;
  padding: 18px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.landing-faq-header:hover {
  text-decoration: underline;
}

.landing-faq-item[data-state="open"] .landing-faq-header {
  color: #FFFFFF;
}

.landing-faq-item .landing-faq-header svg {
  transition: transform 200ms ease;
}

.landing-faq-item[data-state="open"] .landing-faq-header svg {
  transform: rotate(180deg);
}

.landing-faq-content {
  padding: 12px 0 18px;
}

.landing-faq-content p {
  color: #9FB0C8;
}

.landing-faq-header:focus-visible,
.landing-faq-item:focus-visible {
  outline: 3px solid rgba(43, 140, 255, 0.35);
  outline-offset: 3px;
}

.landing-section .landing-section-heading,
.landing-section .landing-section-subheading,
.landing-section .landing-section-title {
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}

.landing-section .landing-card-content,
.landing-section .landing-feature-card,
.landing-section .landing-audience-item {
  text-align: center;
}

.landing-reveal {
  opacity: 0;
  transform: translateY(22px);
  animation: reveal-up 650ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

.landing-reveal:nth-child(2) { animation-delay: 80ms; }
.landing-reveal:nth-child(3) { animation-delay: 160ms; }
.landing-reveal:nth-child(4) { animation-delay: 240ms; }
.landing-reveal:nth-child(5) { animation-delay: 320ms; }

@keyframes reveal-up {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse-glow {
  from { transform: scale(0.96) translate(0, 0); }
  to { transform: scale(1.08) translate(-18px, 14px); }
}

@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  .landing-reveal {
    opacity: 1;
    transform: none;
  }
  .landing-faq-item .landing-faq-header svg {
    transition: none;
  }
}

@media (max-width: 768px) {
  .landing-page {
    overflow-x: hidden;
  }

  .landing-nav {
    padding-left: 0 !important;
    padding-right: 0 !important;
  }

  .landing-nav > div {
    min-height: 64px;
    padding-left: 16px !important;
    padding-right: 16px !important;
  }

  .landing-nav > div > div:last-child {
    gap: 8px;
    margin-left: auto;
  }

  .landing-nav > div > div:last-child > * {
    min-height: 44px;
    font-size: 14px;
  }

  .landing-hero-title {
    letter-spacing: -0.06em !important;
    font-size: clamp(2.25rem, 12vw, 4rem) !important;
  }

  .landing-hero-actions {
    flex-direction: column !important;
    width: 100% !important;
  }

  .landing-hero-actions > * {
    width: 100% !important;
  }

  .landing-section > div {
    padding-left: 20px !important;
    padding-right: 20px !important;
  }
}

@media (min-width: 768px) {
  .landing-hero-title {
    font-size: clamp(3rem, 6vw, 5.5rem) !important;
  }
}
"""
