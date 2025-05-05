# Frontend Guidelines for Financial Advisor App

## Design Philosophy

The Financial Advisor app frontend should adhere to the following guiding principles:

1. **Simplicity First** - Create an interface that makes complex financial concepts accessible
2. **Trust Through Design** - Use design elements that convey professionalism and credibility
3. **Guided Experience** - Lead users through the process with clear navigation and instructions
4. **Responsive & Accessible** - Ensure usability across devices and for users with diverse needs
5. **Visual Communication** - Use data visualization to make financial concepts clear and compelling

## UI Components & Structure

### 1. Landing Page

- **Hero Section**
  - Clear value proposition statement
  - Simple illustration of the portfolio diversification concept
  - Prominent "Get Started" call-to-action
  
- **Key Benefits Section**
  - 3-4 core benefits with simple icons
  - Focus on education, personalization, and privacy
  
- **How It Works**
  - Brief step-by-step visualization of the process
  - Emphasis on simplicity and security

- **Disclaimer Banner**
  - Clear statement about educational purpose
  - Privacy reassurance (no data storage)

### 2. Financial Information Collection

- **Multi-step Form**
  - Progress indicator showing all steps
  - One concept per screen to avoid overwhelming users
  - Clear section headings and field labels
  - Tooltips for explaining financial terms
  
- **Input Validation**
  - Immediate feedback on input errors
  - Helpful suggestions for correction
  - Support for different currency formats

- **Contextual Help**
  - "Why we ask" explanations for sensitive questions
  - Quick definitions for financial terminology
  - Example inputs where helpful

### 3. Risk Assessment Interface

- **Interactive Questionnaire**
  - Visual scenarios for risk tolerance assessment
  - Slider inputs for preference questions
  - Real-time adjustment of risk profile visualization

- **Risk Profile Visualization**
  - Dynamic graphic showing risk-return relationship
  - Clear labeling of the user's position on the spectrum
  - Brief explanation of implications

### 4. Results Dashboard

- **Portfolio Allocation Chart**
  - Interactive pie/donut chart for asset allocation
  - Color-coding system for different asset classes
  - Hover states with additional information

- **Recommendation Cards**
  - Sectioned cards for different aspects of advice
  - Visual hierarchy emphasizing key recommendations
  - Expandable sections for detailed explanations

- **Action Plan Timeline**
  - Visual roadmap for implementing recommendations
  - Milestone indicators for key financial actions
  - Printable/downloadable format

## Visual Design Guidelines

### Color Palette

- **Primary Colors**
  - Deep blue (#1A365D) - Conveys trust and stability
  - Teal accent (#2C7A7B) - Fresh and modern financial approach
  
- **Secondary Colors**
  - Light blue (#63B3ED) - For highlighting and accents
  - Neutral grays (#F7FAFC to #4A5568) - For text and backgrounds
  
- **Data Visualization Colors**
  - Stocks: #3182CE (blue)
  - Bonds: #38A169 (green)
  - Real Estate: #DD6B20 (orange)
  - Cash: #ECC94B (yellow)
  - Alternative: #805AD5 (purple)

### Typography

- **Headings**: Inter or Montserrat (sans-serif)
  - Bold weight for primary headings
  - Clear hierarchy with decreasing sizes

- **Body Text**: Open Sans or Roboto
  - Regular weight for most content
  - 16px minimum size for readability
  - 1.5 line spacing for comfortable reading

- **Data & Numbers**: Roboto Mono or IBM Plex Mono
  - Used for financial figures and percentages
  - Tabular figures for aligned columns

### Iconography

- **Style**: Simple, outline icons with consistent stroke width
- **Purpose**: Use icons to reinforce concepts, not as decoration
- **Accessibility**: Icons should always be accompanied by text labels
- **Recommended sets**: Phosphor Icons, Heroicons, or Feather Icons

## Interaction Guidelines

### Navigation

- **Progress Tracking**
  - Clear "step X of Y" indicators
  - Ability to review previous steps
  - Save and continue later functionality (optional)

- **Transitions**
  - Smooth transitions between sections
  - Loading states for AI processing time
  - Clear "next" and "back" actions

### Form Elements

- **Input Fields**
  - Appropriate input types for different data (number for currency)
  - Descriptive placeholders
  - Field validation with clear error messages
  - Input masks for formatted entries (e.g., percentages)

- **Selection Controls**
  - Radio buttons for single-choice options
  - Checkboxes for multiple selections
  - Dropdowns for options with many choices
  - Sliders for range inputs (e.g., risk tolerance)

### Feedback & States

- **Loading States**
  - Custom loading animations for AI processing
  - Progress indicators for multi-step operations
  - Skeleton screens for content loading

- **Success States**
  - Confirmation messages for completed steps
  - Animation/visual reward for completion
  - Clear next steps guidance

- **Error States**
  - Non-blocking error messages
  - Clear instructions for resolution
  - Graceful fallbacks for technical issues

## Data Visualization Guidelines

### Chart Types

- **Asset Allocation**: Donut chart with interactive segments
- **Risk/Return**: Line chart showing relationship
- **Comparison Scenarios**: Grouped bar charts
- **Time-based Projections**: Area charts with confidence intervals

### Visualization Best Practices

- Start all axes at zero unless specifically inappropriate
- Use consistent colors across the application
- Include legends and clear labels for all data points
- Support interactive exploration (hover, click for details)
- Optimize visualizations for mobile viewing
- Include accessibility features (text alternatives, keyboard navigation)

## Responsiveness Guidelines

### Breakpoints

- **Mobile**: 320px - 480px
- **Tablet**: 481px - 768px
- **Desktop**: 769px - 1279px
- **Large Desktop**: 1280px+

### Mobile Adaptations

- Stack forms vertically
- Simplify charts for smaller screens
- Use collapsible sections for detailed explanations
- Increase touch target sizes (min 44px)
- Consider stepper pattern for multi-step forms

## AI Integration UI Guidelines

### Prompt Display

- Show clearly when AI is generating recommendations
- Provide transparency about what factors the AI is considering
- Use natural language for AI-generated content

### Explanation Interface

- Highlight key factors that influenced recommendations
- Allow users to ask follow-up questions about recommendations
- Provide confidence indicators for different advice elements

## Streamlit-Specific Implementation Notes

- Use `st.columns` for responsive layouts
- Implement `st.form` for collecting related inputs together
- Utilize `st.cache_data` for performance optimization
- Consider `st.tabs` for organizing different sections of results
- Use `st.progress` for indicating AI processing status
- Implement custom CSS with `st.markdown` for styling refinements
- Use `st.session_state` for managing multi-step form state

## Accessibility Considerations

- Maintain WCAG 2.1 AA compliance
- Ensure color contrast meets accessibility standards
- Provide alternative text for all informational images
- Support keyboard navigation for all interactive elements
- Test with screen readers for compatibility
- Use semantic HTML structure in any custom components

This frontend guidelines document provides a comprehensive framework for designing and implementing the Financial Advisor app interface in a way that's intuitive, professional, and effective for users seeking portfolio diversification advice.