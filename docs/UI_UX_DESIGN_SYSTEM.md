# Citadel Design System
## The Fortress of Advanced Capital Allocation

**Brand:** Citadel | **Protocol:** TradeSynapse  
**Theme:** Rick & Morty (Professional Edition)  
**Version:** 1.0  
**Last Updated:** January 30, 2026

---

## 1. DESIGN PHILOSOPHY

### Core Principle
**"Advanced Intelligence Meets Financial Security"**

Citadel's interface reflects:
- 🧠 **Genius-Level Sophistication** (Rick & Morty vibe: advanced tech, dimension-hopping)
- 🏰 **Fortress Security** (Citadel vibe: impenetrable, trustworthy, protective)
- 💼 **Professional Authority** (Finance-grade: clean, serious, no nonsense)
- 🌌 **Sci-Fi Aesthetics** (Portals, infinite intelligence, futuristic)

### Design Pillars
1. **Clarity** - Complex concepts made simple (explain everything)
2. **Trust** - Every pixel builds confidence in your capital
3. **Power** - Advanced features accessible to novices
4. **Consistency** - Same experience everywhere (web, mobile, API)
5. **Delight** - Subtle animations & micro-interactions (no distracting)

---

## 2. COLOR PALETTE

### Primary Colors (Rick & Morty Inspired)

**Portal Blue** (The Wormhole)
```
Primary: #0099FF (Bright cyan-blue)
Light:   #33B4FF
Dark:    #0066CC
RGB:     0, 153, 255
Usage:   Primary CTAs, active states, accents
Emotion: Futuristic, trustworthy, technological
```

**Citadel Purple** (Fortress Power)
```
Primary: #7C3AED (Deep purple)
Light:   #A78BFA
Dark:    #5B21B6
RGB:     124, 58, 237
Usage:   Secondary CTAs, highlights, premium features
Emotion: Power, authority, exclusivity
```

**Dimension Green** (Multi-Chain)
```
Primary: #10B981 (Emerald)
Light:   #6EE7B7
Dark:    #047857
RGB:     16, 185, 129
Usage:   Success states, gains, positive performance
Emotion: Growth, prosperity, flow
```

**Risk Red** (Alert & Danger)
```
Primary: #EF4444 (Bright red)
Light:   #FCA5A5
Dark:    #991B1B
RGB:     239, 68, 68
Usage:   Losses, warnings, critical alerts
Emotion: Urgency, caution, risk awareness
```

### Neutral Colors (Professional Foundation)

**Dark Mode (Default)**
```
Background:    #0F172A (Darkest - nearly black)
Surface:       #1E293B (Card/component background)
Surface 2:     #334155 (Hover states)
Text Primary:  #F1F5F9 (Nearly white)
Text Secondary:#CBD5E1 (Light gray)
Border:        #475569 (Subtle dividers)
```

**Light Mode (Alternative)**
```
Background:    #F8FAFC (Nearly white)
Surface:       #FFFFFF (Pure white)
Surface 2:     #F1F5F9 (Hover states)
Text Primary:  #0F172A (Nearly black)
Text Secondary:#64748B (Medium gray)
Border:        #E2E8F0 (Subtle dividers)
```

### Semantic Colors

| Use Case | Color | Why |
|----------|-------|-----|
| **Profit** | #10B981 (Green) | Growth, gains, positive |
| **Loss** | #EF4444 (Red) | Risk, decline, negative |
| **Pending** | #F59E0B (Amber) | Caution, waiting, neutral |
| **Verified** | #10B981 (Green) | Trust, confirmed, safe |
| **Warning** | #EF4444 (Red) | Attention needed |
| **Info** | #0099FF (Blue) | Educational, helpful |
| **Success** | #10B981 (Green) | Completed, done |

### Color Usage Rules
```
✅ DO:
- Use Portal Blue for primary actions
- Use Dimension Green for gains/profits
- Use Risk Red ONLY for losses/warnings
- Use Citadel Purple for premium features (Pro tier)
- Mix neutrals with one accent color per section

❌ DON'T:
- Use more than 2 accent colors in one view
- Use red for non-critical info (desensitizes users)
- Use colors without sufficient contrast (WCAG AA minimum)
- Use colors alone to convey meaning (always add icons/text)
```

---

## 3. TYPOGRAPHY SYSTEM

### Font Family

**Primary Font:** Inter (Google Fonts)
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
font-feature-settings: 'cv11' 1, 'cv02' 1; /* Better readability */
```

Why Inter?
- Modern, geometric, clean
- Excellent readability at all sizes
- Professional (used by Apple, Figma, Vercel)
- Free & open-source
- Optimized for screens

**Secondary Font:** IBM Plex Mono (Code/Data)
```css
font-family: 'IBM Plex Mono', monospace;
```

Used for:
- Wallet addresses
- Transaction hashes
- Code snippets
- Numeric data (where precision matters)

### Type Scale

| Size | Name | Weight | Line Height | Usage |
|------|------|--------|------------|-------|
| 48px | H1 | 700 Bold | 56px | Page titles |
| 36px | H2 | 700 Bold | 44px | Section headers |
| 28px | H3 | 600 Semi-bold | 36px | Subsection headers |
| 20px | H4 | 600 Semi-bold | 28px | Card titles |
| 16px | Body | 400 Regular | 24px | Body text, paragraphs |
| 14px | Small | 400 Regular | 20px | Labels, descriptions |
| 12px | Tiny | 400 Regular | 18px | Captions, footnotes |

### Font Weights & Styles

```css
/* Font Weights */
Thin:       100 (not used)
ExtraLight: 200 (not used)
Light:      300 (numbers, thin text)
Regular:    400 (body, default)
Medium:     500 (not used)
Semibold:   600 (headers, emphasis)
Bold:       700 (titles, strong emphasis)
ExtraBold:  800 (hero titles, max emphasis)

/* Rarely use more than 400 or 700 */
/* 600 as bridge between regular and bold */
```

### Text Examples

```
H1: "Advanced Capital Allocation"
    font-size: 48px, font-weight: 700, color: #F1F5F9

H2: "Your Performance"
    font-size: 36px, font-weight: 700, color: #F1F5F9

H3: "This Month"
    font-size: 28px, font-weight: 600, color: #CBD5E1

H4: "Total Profit"
    font-size: 20px, font-weight: 600, color: #CBD5E1

Body: "Citadel allocates your capital across..."
    font-size: 16px, font-weight: 400, line-height: 24px, color: #F1F5F9

Label: "Wallet Address"
    font-size: 14px, font-weight: 600, color: #CBD5E1, text-transform: uppercase, letter-spacing: 0.5px

Code: 0x571E52efc50055d760CEaE2446aE3B469a806279
    font-family: IBM Plex Mono, font-size: 12px, color: #0099FF
```

---

## 4. COMPONENT LIBRARY

### Button System

**Primary Button** (Portal Blue - Main actions)
```
State: Default
  Background: #0099FF
  Text: #0F172A (dark)
  Border: none
  Padding: 12px 24px
  Border-radius: 8px
  Font: 16px semi-bold
  
State: Hover
  Background: #0066CC (darker blue)
  Cursor: pointer
  
State: Active
  Background: #0052A3 (even darker)
  Shadow: inset 0 2px 4px rgba(0,0,0,0.2)
  
State: Disabled
  Background: #475569 (gray)
  Opacity: 0.5
  Cursor: not-allowed
```

**Secondary Button** (Citadel Purple - Alternative actions)
```
State: Default
  Background: transparent
  Border: 2px solid #7C3AED
  Text: #7C3AED
  Padding: 10px 22px (adjust for border)
  
State: Hover
  Background: rgba(124, 58, 237, 0.1)
  Border: 2px solid #A78BFA
  
State: Active
  Background: rgba(124, 58, 237, 0.2)
```

**Danger Button** (Risk Red - Destructive actions)
```
State: Default
  Background: #EF4444
  Text: #FFFFFF
  
State: Hover
  Background: #DC2626
  
State: Active
  Background: #991B1B
```

**Icon Button** (Compact actions)
```
Size: 40px × 40px
Icon: 20px × 20px
Border-radius: 6px
Hover: Background: rgba(0, 153, 255, 0.1)
Focus: Outline: 2px solid #0099FF
```

### Input Fields

**Text Input**
```
Default:
  Background: #1E293B
  Border: 1px solid #475569
  Text: #F1F5F9
  Padding: 12px 16px
  Border-radius: 6px
  Font-size: 16px
  
Focus:
  Border: 2px solid #0099FF
  Box-shadow: 0 0 0 3px rgba(0, 153, 255, 0.1)
  
Error:
  Border: 2px solid #EF4444
  Box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1)
  
Placeholder:
  Color: #64748B (gray)
  Font-style: normal
```

**Toggle/Switch**
```
Default Off:
  Background: #334155
  Circle: #64748B
  Size: 44px wide, 24px tall
  
Default On:
  Background: #0099FF
  Circle: #FFFFFF (right side)
  
Animation: 200ms ease-out
```

**Dropdown/Select**
```
Default:
  Border: 1px solid #475569
  Background: #1E293B
  Icon: Chevron down (#CBD5E1)
  
Open:
  Border: 2px solid #0099FF
  Items list with hover effects
  
Item Hover:
  Background: rgba(0, 153, 255, 0.1)
```

### Cards & Containers

**Standard Card**
```
Background: #1E293B
Border: 1px solid #334155
Border-radius: 12px
Padding: 24px
Box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1)

Hover (interactive):
  Border-color: #475569
  Box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15)
  Cursor: pointer
  Transition: 200ms ease-out
```

**Accent Card** (Important info)
```
Same as Standard but:
Border: 2px solid #0099FF
Border-left: 4px solid #0099FF (left accent)
Box-shadow: 0 0 0 1px rgba(0, 153, 255, 0.2)
```

**Stat Card** (Metrics display)
```
Layout:
  Headline: 12px uppercase gray label
  Value: 36px bold Portal Blue number
  Change: 14px regular green/red percentage
  Trend icon: ↑ or ↓
  
Background: #1E293B
Border: 1px solid #334155
Padding: 20px
Border-radius: 12px
```

### Alert/Toast Components

**Info Alert** (Blue)
```
Background: rgba(0, 153, 255, 0.1)
Border-left: 4px solid #0099FF
Icon: ℹ️ (blue)
Text: #F1F5F9
Padding: 16px
Border-radius: 8px
```

**Success Alert** (Green)
```
Background: rgba(16, 185, 129, 0.1)
Border-left: 4px solid #10B981
Icon: ✓ (green)
```

**Warning Alert** (Amber)
```
Background: rgba(245, 158, 11, 0.1)
Border-left: 4px solid #F59E0B
Icon: ⚠️ (amber)
```

**Error Alert** (Red)
```
Background: rgba(239, 68, 68, 0.1)
Border-left: 4px solid #EF4444
Icon: ✕ (red)
```

**Toast** (Bottom-right corner)
```
Similar styling, 4px bottom accent border
Auto-hide after 4 seconds (unless user interaction)
Stack multiple toasts vertically with 8px gaps
```

---

## 5. LAYOUT & SPACING

### Spacing Scale (8px base)

```
0px    - No space
4px    - Micro (icons, minimal gaps)
8px    - Tiny (tight elements)
12px   - Small (labels, small gaps)
16px   - Base (most spacing)
24px   - Medium (sections, cards)
32px   - Large (major sections)
48px   - XL (page sections)
64px   - XXL (hero sections)
```

### Grid System

**Desktop** (1440px max-width)
```
12-column grid
Column width: 80px
Gutter: 24px
Margin: 48px left/right
```

**Tablet** (768px)
```
6-column grid
Column width: 80px
Gutter: 20px
Margin: 24px left/right
```

**Mobile** (375px)
```
4-column grid
Column width: 62px
Gutter: 16px
Margin: 16px left/right
```

### Component Spacing

**Card Container**
```
Padding: 24px
Internal elements gap: 16px
Border-radius: 12px
```

**Buttons in Group**
```
Gap between buttons: 8px
Group to container: 16px margin
```

**Form Fields**
```
Gap between fields: 16px
Label to input: 8px
Help text to input: 4px
```

---

## 6. ANIMATION & MOTION

### Animation Principles

1. **Purpose** - Every animation should clarify or delight (never distract)
2. **Speed** - Faster for feedback (200ms), slower for transitions (400ms)
3. **Easing** - Use ease-out for entrances, ease-in for exits
4. **Restraint** - No animations for the sake of animations

### Easing Functions

```css
/* Smooth, natural feel */
--ease-in:     cubic-bezier(0.4, 0, 1, 1)
--ease-out:    cubic-bezier(0, 0, 0.2, 1)
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)

/* Bouncy (rare, use for delight) */
--ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1)
```

### Standard Animations

**Button Hover** (200ms)
```css
transition: all 200ms ease-out;
Subtle background color shift
Slight scale up (1.02x)
```

**Card Hover** (300ms)
```css
transition: all 300ms ease-out;
Shadow increase
Border color change
```

**Modal Enter** (300ms)
```css
Animation: fade-in + scale-in
From: opacity 0, scale 0.95
To:   opacity 1, scale 1
```

**Modal Exit** (200ms)
```css
Animation: fade-out + scale-out
From: opacity 1, scale 1
To:   opacity 0, scale 0.95
```

**Notification Slide** (300ms)
```css
Animation: slide-in-right
From: translateX(100%)
To:   translateX(0)
```

**Loading Spinner** (Infinite)
```css
Animation: spin
Duration: 1s
Timing: linear
Rotation: 360deg
Color: Portal Blue (#0099FF)
```

**Pulse (for active items)** (2s)
```css
Animation: pulse
From: opacity 1, scale 1
Mid:  opacity 0.8, scale 1.05
To:   opacity 1, scale 1
```

### DO's & DON'Ts

```
✅ DO:
- Use motion to guide attention (success message slide in)
- Use motion to provide feedback (button click animation)
- Keep animations under 300ms (unless intentional delay)
- Use consistent timing across the app
- Provide motion-reduced option (prefers-reduced-motion)

❌ DON'T:
- Animate everything (only interactive elements)
- Use animations longer than 500ms (feels slow)
- Mix easing functions (use consistent easing)
- Animate in/out of focus (use opacity/transform instead)
- Use animations that distract from content
```

---

## 7. ACCESSIBILITY STANDARDS

### Color Contrast

**WCAG AA Standard (minimum):**
```
Normal text: 4.5:1 ratio
Large text:  3:1 ratio
UI elements: 3:1 ratio
```

**Examples:**
```
✅ Portal Blue (#0099FF) on Dark (#0F172A): 6.4:1 PASS
✅ Portal Blue (#0099FF) on Light (#F8FAFC): 8.2:1 PASS
❌ Risk Red (#EF4444) on Dark (#0F172A): 2.8:1 FAIL (too dark)
   Fix: Use brighter red or lighter background
```

### Text Accessibility

- **Minimum font size:** 14px
- **Line height:** At least 1.5x font size
- **Letter spacing:** 0.12em for body text
- **Justified text:** Never (use left-align)
- **Line length:** 60-80 characters max

### Interactive Elements

- **Minimum touch target:** 44px × 44px (mobile)
- **Focus indicator:** Always visible (2px outline)
- **Focus order:** Logical (left-to-right, top-to-bottom)
- **Keyboard shortcuts:** Must have alternative

### Motion & Animations

```css
/* Respect user's motion preferences */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Icons & Images

- **All icons must have text labels** (or aria-label)
- **All images must have alt text**
- **Color alone never conveys meaning** (always use text/icons too)

---

## 8. ICON SYSTEM

### Icon Style

**Style:** Rounded, modern, 24px base size

```
Rules:
- 2px stroke weight (consistent)
- Rounded corners (2px radius)
- No fills (outline only, except special states)
- Consistent padding from bounding box
- Scalable to 16px (small), 32px (large), 48px (hero)
```

### Icon Library

**Recommended:** Heroicons (Tailwind Labs)
- Consistent style
- 24px & 20px variants
- Outline & solid versions
- MIT licensed
- 290+ icons

**Installation:**
```bash
npm install @heroicons/react
```

### Icon Usage

| Icon | Use | Color |
|------|-----|-------|
| Wallet | Cryptocurrency accounts | Portal Blue |
| TrendingUp | Gains/profit | Green |
| TrendingDown | Losses | Red |
| AlertCircle | Warnings/alerts | Amber |
| CheckCircle | Success | Green |
| Clock | Pending/waiting | Amber |
| Lock | Security/vault | Portal Blue |
| Eye | Show/visibility | Gray |
| Settings | Configuration | Gray |
| Menu | Navigation | Gray |

---

## 9. RESPONSIVE DESIGN

### Breakpoints

```css
Mobile:    320px - 639px  (max-width: 639px)
Tablet:    640px - 1023px (min-width: 640px, max-width: 1023px)
Desktop:   1024px+         (min-width: 1024px)
```

### Mobile-First Approach

```css
/* Default: mobile styles */
.card {
  padding: 16px;
  grid-template-columns: 1fr;
}

/* Tablet and up */
@media (min-width: 640px) {
  .card {
    padding: 24px;
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .card {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### Responsive Typography

```css
/* Mobile */
h1 { font-size: 32px; }
h2 { font-size: 24px; }

/* Tablet */
@media (min-width: 640px) {
  h1 { font-size: 40px; }
  h2 { font-size: 32px; }
}

/* Desktop */
@media (min-width: 1024px) {
  h1 { font-size: 48px; }
  h2 { font-size: 36px; }
}
```

### Touch-Friendly Design (Mobile)

- **Minimum touch target:** 44px × 44px
- **Spacing between targets:** At least 8px
- **Avoid small text:** Minimum 16px
- **Avoid hover states** (use active/focus instead)
- **Swipe-friendly:** Full-width interactive areas

---

## 10. DARK MODE & LIGHT MODE

### Dark Mode (Primary)

**Default everywhere.** Dark mode is the hero aesthetic—tech-forward, sophisticated, secure.

```
Background:    #0F172A
Surface:       #1E293B
Text Primary:  #F1F5F9
Text Secondary:#CBD5E1
Accent:        #0099FF (Portal Blue)
```

### Light Mode (Alternative)

**Available but not default.** For accessibility/preference.

```
Background:    #F8FAFC
Surface:       #FFFFFF
Text Primary:  #0F172A
Text Secondary:#64748B
Accent:        #0066CC (Darker Portal Blue for contrast)
```

### Switching Modes

```jsx
// Theme toggle (top-right of nav)
<button onClick={toggleTheme}>
  {isDarkMode ? <Sun /> : <Moon />}
</button>

// Store preference
localStorage.setItem('theme', isDarkMode ? 'dark' : 'light')

// System preference fallback
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
```

---

## 11. COMPONENT STATES & INTERACTIONS

### Loading States

**Skeleton Screens** (preferred over spinners)
```
Replicate component shape with gray placeholders
Subtle pulse animation (opacity fade)
Feels faster than spinners
```

**Spinners** (when uncertain duration)
```
Portal Blue (#0099FF)
24px size (standard)
1s rotation
Used sparingly
```

### Empty States

**No Data**
```
Icon: Large (48px) Portal Blue
Headline: "No strategies yet"
Description: "Create your first strategy..."
CTA Button: "Start Now"
```

### Error States

**Error Message**
```
Alert: Red border, red icon, red text
Inline help: Gray text below field
Form-level: Modal with explanation
```

### Success States

**Confirmation**
```
Toast notification (bottom-right)
Green checkmark icon
Message: "Strategy saved successfully"
Auto-hide after 4 seconds
```

---

## 12. BRAND VOICE & MICROCOPY

### Tone

- **Professional** - Finance-grade language
- **Clear** - No jargon (explain everything)
- **Empowering** - You're in control, not the algorithm
- **Confident** - We know what we're doing
- **Playful** - Rick & Morty references (subtle, rare)

### Example Microcopy

```
Button Labels:
❌ "Execute"          → ✅ "Deploy Strategy"
❌ "Confirm Action"   → ✅ "Approve & Lock"
❌ "Error"            → ✅ "Strategy Failed: Insufficient Funds"

Empty States:
❌ "No data"          → ✅ "No strategies yet. Ready to get started?"

Errors:
❌ "Invalid input"    → ✅ "Wallet address must be 42 characters"

Success:
❌ "Success"          → ✅ "Strategy deployed! You're earning $50/day"
```

### Rick & Morty Easter Eggs (Subtle)

```
Rare, professional references:
- "Citadel of Ricks" modal headline (admin only)
- Dimension toggle emoji: 🌌 (next to chain selector)
- Error message: "That's not a real dimension" (404)
- Loading: "Calculating your dimension-hopping gains..." (rare)

RULES:
- Maximum 1 per page
- Only for users who've been on-platform >1 week
- Professional context (not silly)
- Don't distract from serious operations
```

---

## 13. IMPLEMENTATION CHECKLIST

### Phase 1: Core Design System

**Weeks 1-2:**
- [ ] Tailwind config (colors, fonts, sizes)
- [ ] Component library (buttons, inputs, cards)
- [ ] Layout system (spacing, grid, responsive)
- [ ] Dark mode implementation
- [ ] Accessibility audit

**Weeks 3-4:**
- [ ] Icon system (Heroicons integration)
- [ ] Animation library (transition presets)
- [ ] Form components (all variants)
- [ ] Modal/dialog system
- [ ] Notification system (toast, alerts)

**Weeks 5+:**
- [ ] Page templates (dashboard, strategy, wallet, etc.)
- [ ] Component storybook (Storybook.js)
- [ ] Design documentation website
- [ ] Figma design tokens export
- [ ] Component audit & polish

### Phase 2: Advanced Components

- [ ] Data tables (sortable, filterable)
- [ ] Charts & graphs (Recharts)
- [ ] Calendar/date pickers
- [ ] Dropdown menus with keyboard support
- [ ] Advanced forms (multi-step, conditional)

---

## 14. TOOLING & RESOURCES

### Frontend Framework
- **Next.js 16** (React 18, TypeScript)
- **Tailwind CSS 3.4** (styling)
- **Headless UI** (accessible components)

### Component Libraries
- **Heroicons** (icons)
- **Recharts** (charts)
- **React Hook Form** (forms)
- **Framer Motion** (animations)

### Design Tools
- **Figma** (design, prototyping, handoff)
- **Storybook** (component documentation)
- **Playwright** (visual regression testing)

### Accessibility Tools
- **axe DevTools** (browser extension)
- **WAVE** (color contrast checker)
- **Screen reader testing** (NVDA, VoiceOver)

---

## 15. FILE STRUCTURE

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/                    (Base components)
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Alert.tsx
│   │   │   ├── Toast.tsx
│   │   │   └── Modal.tsx
│   │   │
│   │   ├── layout/                (Page layout)
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   │
│   │   └── features/              (Feature-specific)
│   │       ├── WalletCard.tsx
│   │       ├── StrategyCard.tsx
│   │       └── PerformanceChart.tsx
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   ├── animations.css
│   │   └── variables.css
│   │
│   ├── lib/
│   │   ├── cn.ts                  (className merge)
│   │   └── constants.ts           (colors, spacing, etc.)
│   │
│   └── pages/
│       ├── dashboard.tsx
│       ├── strategies.tsx
│       ├── wallets.tsx
│       └── settings.tsx
│
└── tailwind.config.js            (Design system config)
```

---

## 16. NEXT STEPS

1. **Implement Tailwind Config** (design tokens)
2. **Create Component Library** (Storybook)
3. **Build Page Templates** (dashboard, strategy, wallet)
4. **Add Animations** (Framer Motion)
5. **Accessibility Audit** (axe, WAVE, screen reader)
6. **Design QA** (review all pages, consistency check)

---

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Heroicons](https://heroicons.com)
- [Web Content Accessibility Guidelines (WCAG)](https://www.w3.org/WAI/WCAG21/quickref/)
- [Design System Best Practices](https://www.designsystems.com)
- [Framer Motion Documentation](https://www.framer.com/motion/)

---

**Status:** Design System Complete  
**Next:** Implement in Tailwind Config + Component Library  
**Questions?** Ask before moving forward
