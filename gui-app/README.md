# Seismic Dashboard GUI Application

A modern, interactive web application for real-time seismic event monitoring and analysis built with React, TypeScript, and modern web technologies.

## ✨ Features

- **Real-time Monitoring**: Live seismic waveform visualization and event detection
- **Interactive Dashboard**: Comprehensive overview with statistics and recent events
- **Data Analysis**: Advanced charts and visualizations for seismic data analysis
- **Event Classification**: AI-powered classification of seismic events (earthquakes, explosions, volcanic, noise)
- **File Upload**: Support for SAC, MiniSEED, CSV, and JSON seismic data files
- **Notifications**: Real-time alerts for significant seismic events
- **Modern UI**: Responsive design with dark/light theme support
- **Data Export**: Export analysis results to CSV format

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Modern web browser

### Installation & Launch

1. **Clone and Navigate**:
   ```bash
   git clone https://github.com/hkevin01/seismic-classifier.git
   cd seismic-classifier/gui-app
   ```

2. **Quick Launch** (Automated):
   ```bash
   chmod +x launch.sh
   ./launch.sh
   ```

3. **Manual Setup**:
   ```bash
   npm install
   npm run dev
   ```

4. **Open Browser**:
   Navigate to `http://localhost:3000`

## 🏗️ Architecture

### Technology Stack
- **Frontend**: React 18.2.0 with TypeScript
- **Build Tool**: Vite 5.0.8 with hot module replacement
- **Styling**: Tailwind CSS 3.4.0 with custom design system
- **State Management**: Zustand 4.4.7 for lightweight state management
- **Animations**: Framer Motion 10.16.16 for smooth transitions
- **Data Visualization**: Recharts 2.10.3 for interactive charts
- **Routing**: React Router 6.8.0 for client-side navigation
- **Icons**: Lucide React for modern SVG icons
- **File Upload**: React Dropzone for drag-and-drop file handling

### Project Structure
```
gui-app/
├── src/
│   ├── components/
│   │   ├── ui/           # Reusable UI components
│   │   ├── layout/       # Layout components (Sidebar, Header)
│   │   ├── charts/       # Data visualization components
│   │   └── modals/       # Modal dialogs
│   ├── pages/            # Main application pages
│   ├── store/            # Zustand state management
│   └── styles/           # Global styles and Tailwind config
├── public/               # Static assets
└── config files          # Vite, TypeScript, ESLint configs
```

## 📊 Application Features

### Dashboard
- **Statistics Cards**: Real-time event counts, magnitude averages, and system status
- **Recent Events**: Live updating list of latest seismic events
- **Quick Actions**: Fast access to monitoring controls and file uploads
- **System Overview**: Connection status and monitoring health

### Real-time Monitoring
- **Live Waveform**: Continuous seismic signal visualization
- **Station Network**: Status monitoring of connected seismic stations
- **Event Detection**: Real-time classification and alerting
- **Historical Timeline**: Events over time with filtering capabilities

### Data Analysis
- **Magnitude Distribution**: Bar charts showing earthquake magnitude patterns
- **Event Timeline**: Historical trends and pattern analysis
- **Classification Breakdown**: Pie charts of event types
- **Depth vs Magnitude**: Scatter plots for geological analysis
- **Data Export**: CSV export functionality for further analysis

### File Management
- **Multi-format Support**: SAC, MiniSEED, CSV, JSON file uploads
- **Drag & Drop**: Modern file upload interface
- **Progress Tracking**: Real-time upload progress and status
- **Batch Processing**: Handle multiple files simultaneously

## 🎨 UI/UX Features

### Design System
- **Glass-effect Styling**: Modern translucent card designs
- **Gradient Accents**: Beautiful color gradients throughout
- **Responsive Layout**: Mobile-first responsive design
- **Dark/Light Theme**: Automatic theme switching support
- **Smooth Animations**: Framer Motion powered transitions

### Interactive Elements
- **Hover Effects**: Subtle animations on user interaction
- **Loading States**: Skeleton loading and progress indicators
- **Modal Dialogs**: Settings, notifications, and user management
- **Toast Notifications**: Non-intrusive real-time alerts
- **Navigation**: Intuitive sidebar with active state indicators

## 🔧 Development

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues

### Configuration
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency rules
- **Tailwind**: Utility-first CSS with custom design tokens
- **Vite**: Fast build tool with hot module replacement

## 📈 Data Flow

1. **Event Generation**: Simulated real-time seismic events
2. **State Management**: Zustand store for centralized data
3. **Real-time Updates**: Live dashboard and chart updates
4. **User Interactions**: Modal dialogs and settings management
5. **Data Persistence**: Local storage for user preferences

## 🌐 Browser Support

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## 📝 License

This project is part of the seismic-classifier repository. See the main repository for licensing information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📞 Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/hkevin01/seismic-classifier/issues)
- Check the main repository documentation

---

**Built with ❤️ for seismic research and monitoring**
