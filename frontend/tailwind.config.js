/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Material Design 3 Color System
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        
        // Google Material Design 3 Primary Colors
        primary: {
          DEFAULT: "#1A73E8", // Google Blue
          50: "#E3F2FD",
          100: "#BBDEFB", 
          200: "#90CAF9",
          300: "#64B5F6",
          400: "#42A5F5",
          500: "#1A73E8",
          600: "#1565C0",
          700: "#0D47A1",
          800: "#0A3D91",
          900: "#062E6F",
          foreground: "#FFFFFF",
        },
        
        // Google Green
        secondary: {
          DEFAULT: "#34A853", // Google Green
          50: "#E8F5E8",
          100: "#C8E6C9",
          200: "#A5D6A7",
          300: "#81C784",
          400: "#66BB6A",
          500: "#34A853",
          600: "#2E7D32",
          700: "#1B5E20",
          800: "#145239",
          900: "#0D4125",
          foreground: "#FFFFFF",
        },
        
        // Google Red for warnings/errors
        error: {
          DEFAULT: "#EA4335", // Google Red
          50: "#FFEBEE",
          100: "#FFCDD2",
          200: "#EF9A9A",
          300: "#E57373",
          400: "#EF5350",
          500: "#EA4335",
          600: "#E53935",
          700: "#D32F2F",
          800: "#C62828",
          900: "#B71C1C",
          foreground: "#FFFFFF",
        },
        
        // Google Yellow
        warning: {
          DEFAULT: "#FBBC04", // Google Yellow
          50: "#FFFDE7",
          100: "#FFF9C4",
          200: "#FFF59D",
          300: "#FFF176",
          400: "#FFEE58",
          500: "#FBBC04",
          600: "#FBC02D",
          700: "#F9A825",
          800: "#F57F17",
          900: "#FF6F00",
          foreground: "#000000",
        },
      },
      
      borderRadius: {
        xs: "4px",
        sm: "8px", 
        md: "12px",
        lg: "16px",
        xl: "20px",
        "2xl": "28px",
        full: "1000px",
      },
      
      fontFamily: {
        sans: ['Google Sans', 'Roboto', 'system-ui', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      
      fontSize: {
        // Material Design 3 Typography Scale
        'display-large': ['57px', { lineHeight: '64px', fontWeight: '400' }],
        'display-medium': ['45px', { lineHeight: '52px', fontWeight: '400' }],
        'display-small': ['36px', { lineHeight: '44px', fontWeight: '400' }],
        'headline-large': ['32px', { lineHeight: '40px', fontWeight: '400' }],
        'headline-medium': ['28px', { lineHeight: '36px', fontWeight: '400' }],
        'headline-small': ['24px', { lineHeight: '32px', fontWeight: '400' }],
        'title-large': ['22px', { lineHeight: '28px', fontWeight: '500' }],
        'title-medium': ['16px', { lineHeight: '24px', fontWeight: '500' }],
        'title-small': ['14px', { lineHeight: '20px', fontWeight: '500' }],
        'label-large': ['14px', { lineHeight: '20px', fontWeight: '500' }],
        'label-medium': ['12px', { lineHeight: '16px', fontWeight: '500' }],
        'label-small': ['11px', { lineHeight: '16px', fontWeight: '500' }],
        'body-large': ['16px', { lineHeight: '24px', fontWeight: '400' }],
        'body-medium': ['14px', { lineHeight: '20px', fontWeight: '400' }],
        'body-small': ['12px', { lineHeight: '16px', fontWeight: '400' }],
      },
      
      boxShadow: {
        // Material Design 3 Elevation System
        'elevation-1': '0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)',
        'elevation-2': '0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15)',
        'elevation-3': '0px 4px 8px 3px rgba(0, 0, 0, 0.15), 0px 1px 3px 0px rgba(0, 0, 0, 0.3)',
        'elevation-4': '0px 6px 10px 4px rgba(0, 0, 0, 0.15), 0px 2px 3px 0px rgba(0, 0, 0, 0.3)',
        'elevation-5': '0px 8px 12px 6px rgba(0, 0, 0, 0.15), 0px 4px 4px 0px rgba(0, 0, 0, 0.3)',
      },
      
      animation: {
        // Material Motion animations
        'fade-in': 'fadeIn 200ms cubic-bezier(0.2, 0, 0, 1)',
        'fade-out': 'fadeOut 150ms cubic-bezier(0.4, 0, 1, 1)',
        'slide-in': 'slideIn 300ms cubic-bezier(0.2, 0, 0, 1)',
        'slide-out': 'slideOut 200ms cubic-bezier(0.4, 0, 1, 1)',
        'scale-in': 'scaleIn 200ms cubic-bezier(0.2, 0, 0, 1)',
        'scale-out': 'scaleOut 150ms cubic-bezier(0.4, 0, 1, 1)',
        'ripple': 'ripple 600ms cubic-bezier(0.4, 0, 0.2, 1)',
      },
      
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideIn: {
          '0%': { transform: 'translateY(16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideOut: {
          '0%': { transform: 'translateY(0)', opacity: '1' },
          '100%': { transform: 'translateY(-16px)', opacity: '0' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        scaleOut: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(0.9)', opacity: '0' },
        },
        ripple: {
          '0%': { transform: 'scale(0)', opacity: '1' },
          '100%': { transform: 'scale(4)', opacity: '0' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
