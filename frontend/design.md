# Aerointel Solutions Frontend Design System

## Overview
The Aerointel Solutions frontend features a comprehensive design system built on Material-UI with extensive customization capabilities. This design system supports multiple themes, layouts, and responsive design patterns for an enterprise AI knowledge management platform.

## Core Design Architecture

### Theme System (`src/theme/`)

#### Color System
- **Primary Colors**: 6 color options (blue, cyan, purple, orange, red, pink)
- **Semantic Colors**: info, success, warning, error with complete color scales
- **Grey Scale**: 10-level grey palette (50-900)
- **Alpha System**: Dynamic transparency using CSS variables
- **Dark/Light Mode**: Full theme switching support

**Files:**
- `src/theme/core/colors.json` - Main color palette definitions
- `src/theme/with-settings/primary-color.json` - Alternative primary color themes
- `src/theme/core/palette.ts` - Color configuration with mode support

#### Typography System
- **Font Stack**: Public Sans (primary), Barlow, DM Sans, Inter, Nunito Sans
- **Type Scale**: h1-h6, subtitle1-2, body1-2, caption, overline, button
- **Responsive Sizing**: Breakpoint-specific font scaling
- **Weight Variants**: 400 (Regular), 600 (SemiBold), 700 (Bold), 800 (ExtraBold)

**File:** `src/theme/core/typography.ts`

#### Advanced Styling
- **Utility Functions**: pxToRem, responsiveFontSizes, varAlpha, hexToRgbChannel
- **Mixins**: textGradient, borderGradient, bgBlur, maxLine, paper effects
- **Custom Shadows**: Elevation system with color-aware shadows

**Files:**
- `src/theme/styles/utils.ts` - Theme utilities
- `src/theme/styles/mixins.ts` - Advanced styling mixins
- `src/theme/core/custom-shadows.ts` - Shadow system

### Component Design System

#### Material-UI Overrides (`src/theme/core/components/`)
Complete theming for 35+ Material-UI components including:

**Form Components:**
- Button (4 variants: contained, outlined, text, soft)
- TextField with consistent styling
- Autocomplete with custom dropdown
- Checkbox, Radio, Switch with brand colors
- Select with enhanced dropdown styling

**Layout Components:**
- Card with elevation and hover effects
- Dialog with backdrop blur
- Drawer with navigation styling
- AppBar with transparent variants

**Data Display:**
- Table with zebra striping and hover states
- DataGrid with custom cell styling
- Chip with 4 color variants
- Avatar with size variants

**Navigation:**
- Tabs with indicator styling
- Breadcrumbs with separator icons
- Pagination with rounded buttons

**Feedback:**
- Alert with icon and action styling
- Skeleton with wave animation
- Progress indicators

#### Custom Component Library (`src/components/`)

**Animation System** (`src/components/animate/`)
- **Variants**: fade, slide, zoom, bounce, rotate, scale
- **Framer Motion Integration**: Smooth transitions and micro-interactions
- **Components**: MotionContainer, MotionViewport, AnimateCountUp, AnimateAvatar

**Navigation Components**
- **NavSection**: Hierarchical navigation with bullet points and active states
- **NavBasic**: Simple navigation for mobile/desktop
- **Support**: Vertical, horizontal, and mini layouts

**Visual Components**
- **Logo**: SVG component with theme-adaptive colors
- **Label**: 4 variants (filled, outlined, soft, inverted)
- **Iconify**: 100+ themed icons with color support
- **Image**: Enhanced component with lazy loading

**Interactive Components**
- **Carousel**: Multi-breakpoint slider with dots, arrows, progress
- **Editor**: Rich text editor with syntax highlighting
- **Chart**: Recharts integration with theme colors
- **Custom Tabs**: Enhanced tab component

**Utility Components**
- **Scrollbar**: Custom styled scrollbars
- **Loading Screen**: Splash screen and loading states
- **Empty Content**: Consistent empty state designs
- **Search Not Found**: Search result empty states

### Layout System (`src/layouts/`)

#### Layout Types
1. **Dashboard Layout**: Main application layout with navigation
2. **Auth Centered**: Center-aligned authentication forms
3. **Auth Split**: Split-screen authentication with branding
4. **Simple Layout**: Minimal layout for basic pages

#### Navigation Patterns
- **Vertical Navigation**: Sidebar with hierarchical menu
- **Horizontal Navigation**: Top-bar navigation
- **Mini Navigation**: Collapsed sidebar with icons
- **Mobile Navigation**: Responsive drawer navigation

**Files:**
- `src/layouts/classes.ts` - Layout CSS classes
- `src/layouts/dashboard/styles.ts` - Dashboard styling
- `src/layouts/components/` - Reusable layout components

### Settings & Customization (`src/components/settings/`)

#### Theme Configuration Options
- **Color Schemes**: 6 primary colors + custom
- **Layout Modes**: Vertical, horizontal, mini navigation
- **Appearance**: Light, dark, system mode
- **Fonts**: 5 font family options
- **Direction**: LTR/RTL support

**Components:**
- Settings drawer with live preview
- Color picker with presets
- Layout mode switcher
- Font family selector

### Asset Management

#### Icons (`public/assets/icons/`)
- **Home Icons**: design, development, brand
- **Navbar Icons**: chat, dashboard, disabled states
- **Notification Icons**: chat, delivery, mail, order
- **Platform Icons**: JWT, authentication providers

#### Branding (`public/logo/`)
- **Logo Variants**: blue, full, single, signin page
- **Brand Colors**: Consistent with theme system
- **Welcome Assets**: GIF animations

#### Fonts (`public/fonts/`)
- **Roboto**: Regular, Bold weights
- **Font Loading**: Optimized @fontsource imports

### Responsive Design

#### Breakpoint System
- **xs**: 0px+
- **sm**: 600px+
- **md**: 900px+
- **lg**: 1200px+
- **xl**: 1536px+

#### Mobile-First Approach
- Progressive enhancement
- Touch-friendly interfaces
- Responsive typography
- Adaptive layouts

### Feature-Specific Design

#### Authentication Design (`src/auth/styles/`)
- Card-based layouts
- Tab navigation styling
- Social login buttons with brand colors
- Method configuration forms

#### Chat Interface (`src/sections/qna/chatbot/`)
- **Message Styling**: User/assistant differentiation
- **Citations**: Hover cards with source information
- **Syntax Highlighting**: Code block styling
- **PDF Viewer**: Embedded document viewer
- **Feedback System**: Thumbs up/down with animations

#### Knowledge Base (`src/sections/knowledgebase/`)
- **Search Interface**: Advanced search with filters
- **Record Cards**: Document preview cards
- **Detail Views**: Full document display
- **Sidebar Navigation**: Contextual navigation

#### Account Settings (`src/sections/accountdetails/`)
- **Form Layouts**: Multi-step configuration
- **Service Cards**: External service configuration
- **Group Management**: User and group interfaces
- **Profile Forms**: Personal and company profiles

### CSS Architecture

#### Global Styles (`src/global.css`)
- Font loading optimization
- Component CSS imports
- Baseline HTML/body styles
- List and image defaults

#### CSS Variables System
- Dynamic color channels
- Theme-aware properties
- Dark/light mode switching
- Component-specific variables

#### Style Organization
- Component-scoped styles
- Utility classes
- Theme-aware mixins
- Responsive utilities

### Design Tokens

#### Color Tokens
- Primary: 6 brand color options
- Semantic: success, warning, error, info
- Neutral: 10-level grey scale
- Alpha: Transparency variants

#### Spacing Tokens
- Base unit: 8px
- Scale: 0.5x to 10x multipliers
- Consistent margin/padding

#### Typography Tokens
- Font sizes: 12px to 48px
- Line heights: 1.2 to 1.8
- Letter spacing: -0.5px to 2px

#### Border Radius Tokens
- None: 0px
- Small: 4px
- Medium: 8px
- Large: 12px
- XL: 16px
- Full: 50%

### Animation Guidelines

#### Motion Principles
- **Duration**: 200-500ms for micro-interactions
- **Easing**: Material Design curves
- **Performance**: Transform and opacity only
- **Accessibility**: Respect prefers-reduced-motion

#### Animation Types
- **Fade**: Opacity transitions
- **Slide**: Transform translations
- **Scale**: Size transformations
- **Bounce**: Elastic animations
- **Rotate**: Rotation effects

### Accessibility Features

#### Color Accessibility
- WCAG AA contrast ratios
- Color-blind friendly palettes
- Focus indicators
- High contrast mode support

#### Navigation Accessibility
- Keyboard navigation
- ARIA labels and roles
- Screen reader support
- Focus management

#### Component Accessibility
- Semantic HTML
- Form validation feedback
- Loading states
- Error handling

### Performance Optimizations

#### Asset Loading
- Font preloading
- Lazy image loading
- Icon optimization
- Bundle splitting

#### Runtime Performance
- Memoized components
- Efficient re-renders
- Optimized animations
- Debounced interactions

### Design System Usage

#### Getting Started
```tsx
import { ThemeProvider } from 'src/theme';
import { SettingsProvider } from 'src/components/settings';

function App() {
  return (
    <SettingsProvider>
      <ThemeProvider>
        {/* Your app */}
      </ThemeProvider>
    </SettingsProvider>
  );
}
```

#### Component Examples
```tsx
// Using theme colors
<Button variant="contained" color="primary">
  Primary Button
</Button>

// Using custom variants
<Button variant="soft" color="info">
  Soft Info Button
</Button>

// Using animations
<MotionViewport>
  <Box variants={varFade().inUp}>
    Animated Content
  </Box>
</MotionViewport>
```

#### Customization
```tsx
// Custom theme configuration
const settings = {
  themeMode: 'dark',
  themeColorScheme: 'purple',
  themeLayout: 'horizontal',
  themeFont: 'inter'
};
```

### Future Enhancements

#### Planned Features
- Component documentation site
- Design token JSON exports
- Figma design system integration
- A11y testing automation
- Performance monitoring

#### Maintenance Guidelines
- Regular dependency updates
- Design system audits
- Performance testing
- Accessibility reviews
- User feedback integration

---

**Last Updated**: 2025-07-19
**Version**: 2.0
**Maintainers**: Aerointel Solutions Team