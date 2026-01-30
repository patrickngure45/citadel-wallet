/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // Use class-based dark mode
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // ═══════════════════════════════════════════════════════════════════
      // COLORS - Citadel Design System
      // ═══════════════════════════════════════════════════════════════════
      colors: {
        // Portal Blue (Primary)
        portal: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c3d66',
          // Custom for Citadel
          primary: '#0099FF',
          light: '#33B4FF',
          dark: '#0066CC',
        },

        // Citadel Purple (Secondary)
        citadel: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
          // Custom for Citadel
          primary: '#7C3AED',
          light: '#A78BFA',
          dark: '#5B21B6',
        },

        // Dimension Green (Success)
        dimension: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#145231',
          // Custom for Citadel
          primary: '#10B981',
          light: '#6EE7B7',
          dark: '#047857',
        },

        // Risk Red (Danger)
        risk: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          // Custom for Citadel
          primary: '#EF4444',
          light: '#FCA5A5',
          dark: '#991B1B',
        },

        // Neutrals (Dark Mode Default)
        dark: {
          bg: '#0F172A',          // Background
          surface: '#1E293B',     // Card/component
          surface2: '#334155',    // Hover states
          border: '#475569',      // Dividers
          text: '#F1F5F9',        // Primary text
          'text-secondary': '#CBD5E1', // Secondary text
        },

        // Neutrals (Light Mode)
        light: {
          bg: '#F8FAFC',
          surface: '#FFFFFF',
          surface2: '#F1F5F9',
          border: '#E2E8F0',
          text: '#0F172A',
          'text-secondary': '#64748B',
        },

        // Semantic colors
        success: '#10B981',
        warning: '#F59E0B',
        info: '#0099FF',
        error: '#EF4444',
      },

      // ═══════════════════════════════════════════════════════════════════
      // TYPOGRAPHY
      // ═══════════════════════════════════════════════════════════════════
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace'],
      },

      fontSize: {
        // Custom type scale
        xs: ['12px', { lineHeight: '18px', letterSpacing: '0px' }],
        sm: ['14px', { lineHeight: '20px', letterSpacing: '0px' }],
        base: ['16px', { lineHeight: '24px', letterSpacing: '0px' }],
        lg: ['18px', { lineHeight: '28px', letterSpacing: '0px' }],
        xl: ['20px', { lineHeight: '28px', letterSpacing: '0px' }],
        '2xl': ['24px', { lineHeight: '32px', letterSpacing: '0px' }],
        '3xl': ['30px', { lineHeight: '36px', letterSpacing: '0px' }],
        '4xl': ['36px', { lineHeight: '44px', letterSpacing: '0px' }],
        '5xl': ['48px', { lineHeight: '56px', letterSpacing: '0px' }],
      },

      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
      },

      // ═══════════════════════════════════════════════════════════════════
      // SPACING - 8px base
      // ═══════════════════════════════════════════════════════════════════
      spacing: {
        0: '0px',
        1: '4px',
        2: '8px',
        3: '12px',
        4: '16px',
        5: '20px',
        6: '24px',
        7: '28px',
        8: '32px',
        9: '36px',
        10: '40px',
        11: '44px',
        12: '48px',
        13: '52px',
        14: '56px',
        15: '60px',
        16: '64px',
      },

      // ═══════════════════════════════════════════════════════════════════
      // BORDER RADIUS
      // ═══════════════════════════════════════════════════════════════════
      borderRadius: {
        none: '0px',
        sm: '4px',
        DEFAULT: '6px',
        md: '8px',
        lg: '12px',
        xl: '16px',
        '2xl': '20px',
        full: '9999px',
      },

      // ═══════════════════════════════════════════════════════════════════
      // SHADOWS - Professional depth
      // ═══════════════════════════════════════════════════════════════════
      boxShadow: {
        none: 'none',
        xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        base: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        // Glow effects (Portal Blue)
        glow: '0 0 20px rgba(0, 153, 255, 0.3)',
        'glow-lg': '0 0 40px rgba(0, 153, 255, 0.5)',
      },

      // ═══════════════════════════════════════════════════════════════════
      // ANIMATIONS
      // ═══════════════════════════════════════════════════════════════════
      keyframes: {
        // Fade animations
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-out': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },

        // Slide animations
        'slide-in-right': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'slide-out-right': {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(100%)' },
        },
        'slide-in-left': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'slide-in-up': {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },

        // Scale animations
        'scale-in': {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'scale-out': {
          '0%': { opacity: '1', transform: 'scale(1)' },
          '100%': { opacity: '0', transform: 'scale(0.95)' },
        },

        // Pulse animation
        pulse: {
          '0%': { opacity: '1' },
          '50%': { opacity: '0.8' },
          '100%': { opacity: '1' },
        },

        // Spin animation (loading)
        spin: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },

        // Bounce animation
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },

        // Glow pulse
        'glow-pulse': {
          '0%, 100%': {
            boxShadow: '0 0 20px rgba(0, 153, 255, 0.3)',
          },
          '50%': {
            boxShadow: '0 0 40px rgba(0, 153, 255, 0.6)',
          },
        },
      },

      animation: {
        // Fast animations (UI feedback)
        'fade-in': 'fade-in 200ms ease-out',
        'fade-out': 'fade-out 200ms ease-in',
        'scale-in': 'scale-in 200ms ease-out',
        'scale-out': 'scale-out 200ms ease-in',

        // Medium animations (transitions)
        'slide-in-right': 'slide-in-right 300ms ease-out',
        'slide-out-right': 'slide-out-right 300ms ease-in',
        'slide-in-left': 'slide-in-left 300ms ease-out',
        'slide-in-up': 'slide-in-up 300ms ease-out',

        // Loading
        'spin': 'spin 1s linear infinite',
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce': 'bounce 1s infinite',

        // Glow effects
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
      },

      // ═══════════════════════════════════════════════════════════════════
      // TRANSITIONS
      // ═══════════════════════════════════════════════════════════════════
      transitionDuration: {
        0: '0ms',
        75: '75ms',
        100: '100ms',
        150: '150ms',
        200: '200ms',
        300: '300ms',
        500: '500ms',
        700: '700ms',
        1000: '1000ms',
      },

      transitionTimingFunction: {
        'ease-in': 'cubic-bezier(0.4, 0, 1, 1)',
        'ease-out': 'cubic-bezier(0, 0, 0.2, 1)',
        'ease-in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },

      // ═══════════════════════════════════════════════════════════════════
      // BREAKPOINTS (Mobile-first)
      // ═══════════════════════════════════════════════════════════════════
      screens: {
        sm: '640px',   // Tablet
        md: '768px',   // Tablet large
        lg: '1024px',  // Desktop
        xl: '1280px',  // Desktop large
        '2xl': '1536px', // Desktop XL
      },

      // ═══════════════════════════════════════════════════════════════════
      // CUSTOM UTILITIES
      // ═══════════════════════════════════════════════════════════════════
      backgroundImage: {
        'gradient-portal': 'linear-gradient(135deg, #0099FF 0%, #0066CC 100%)',
        'gradient-citadel': 'linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%)',
        'gradient-dimension': 'linear-gradient(135deg, #10B981 0%, #047857 100%)',
      },

      // Ring/outline for focus states
      outlineColor: {
        portal: '#0099FF',
        citadel: '#7C3AED',
      },

      // ═══════════════════════════════════════════════════════════════════
      // MIN/MAX WIDTH
      // ═══════════════════════════════════════════════════════════════════
      maxWidth: {
        'container-sm': '640px',
        'container-md': '768px',
        'container': '1024px',
        'container-lg': '1280px',
        'container-xl': '1440px',
      },
    },
  },

  plugins: [
    // Custom plugin for responsive grid
    function ({ addComponents }) {
      addComponents({
        // Utility classes
        '.text-truncate': {
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        },
        '.line-clamp-2': {
          display: '-webkit-box',
          '-webkit-line-clamp': '2',
          '-webkit-box-orient': 'vertical',
          overflow: 'hidden',
        },
        '.line-clamp-3': {
          display: '-webkit-box',
          '-webkit-line-clamp': '3',
          '-webkit-box-orient': 'vertical',
          overflow: 'hidden',
        },

        // Focus ring (accessibility)
        '.focus-ring': {
          '@apply outline-2 outline-offset-2 outline-portal': {},
        },

        // Card base styles
        '.card': {
          '@apply rounded-lg border border-slate-700 bg-slate-800 p-6 shadow-sm transition-all duration-200': {},
          '&:hover': {
            '@apply border-slate-600 shadow-md': {},
          },
        },

        '.card-interactive': {
          '@apply cursor-pointer': {},
          '&:hover': {
            '@apply bg-slate-700': {},
          },
        },

        // Button base styles
        '.btn': {
          '@apply inline-flex items-center justify-center gap-2 rounded-md px-4 py-2 font-semibold transition-all duration-200 focus-ring': {},
        },

        '.btn-primary': {
          '@apply btn bg-portal-primary text-slate-900 hover:bg-portal-dark': {},
        },

        '.btn-secondary': {
          '@apply btn border-2 border-citadel-primary bg-transparent text-citadel-primary hover:bg-citadel-primary hover:text-white': {},
        },

        '.btn-danger': {
          '@apply btn bg-risk-primary text-white hover:bg-risk-dark': {},
        },

        // Badge styles
        '.badge': {
          '@apply inline-flex items-center rounded-full px-3 py-1 text-sm font-medium': {},
        },

        '.badge-success': {
          '@apply bg-dimension-primary/20 text-dimension-light': {},
        },

        '.badge-warning': {
          '@apply bg-yellow-500/20 text-yellow-300': {},
        },

        '.badge-danger': {
          '@apply bg-risk-primary/20 text-risk-light': {},
        },

        // Input base styles
        '.input': {
          '@apply w-full rounded-md border border-slate-600 bg-slate-700 px-4 py-2 text-white placeholder-slate-400 transition-all focus:border-portal-primary focus:outline-none focus:ring-2 focus:ring-portal-primary/30': {},
        },

        // Disabled state
        '.disabled': {
          '@apply cursor-not-allowed opacity-50': {},
        },
      });
    },

    // Respects prefers-reduced-motion
    function ({ addBase, e, theme }) {
      addBase({
        '@media (prefers-reduced-motion: reduce)': {
          '*': {
            'animation-duration': '0.01ms !important',
            'animation-iteration-count': '1 !important',
            'transition-duration': '0.01ms !important',
          },
        },
      });
    },
  ],
};
