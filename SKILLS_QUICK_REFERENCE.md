# 🚀 Skills Network & Analysis - Quick Reference

## 🎯 Quick Start

1. **Start the Server**: `python web_dashboard/app.py` (runs on http://localhost:5002)
2. **Search Jobs**: Enter keywords, location, select sources
3. **View Analysis**: Click "📊 Skills Analysis" tab
4. **Explore Network**: Click "🌐 Skills Network" tab

## 📊 Skills Analysis Tab

### What It Shows
- **Bar Chart**: Top 10 skills by frequency
- **Skills Table**: All skills ranked with frequency counts
- **Debug Info**: Technical details

### How to Use
1. Perform a job search first
2. Click "📊 Skills Analysis" tab
3. View automatically generated charts and tables
4. Interpret frequency data and skill rankings

## 🌐 Skills Network Tab

### What It Shows
- **Interactive Network**: Skills as nodes, connections as edges
- **Node Size**: Larger = more frequent skills
- **Node Colors**: Red (high demand) → Green (lower demand)
- **Connections**: Lines showing skill co-occurrences

### Controls
- **Min Skill Frequency**: Filter by minimum mentions
- **Min Co-occurrence**: Filter by connection strength
- **Keyword Filter**: Search for specific skills
- **Experience Level**: Filter by job level
- **🔄 Update Network**: Apply filters
- **🔄 Reset**: Clear all filters
- **📊 Show Experience Distribution**: View level breakdown

### Interactions
- **Click Node**: Highlight connections
- **Hover Node**: Show skill details
- **Drag Node**: Rearrange layout
- **Zoom**: Mouse wheel or pinch
- **Double-click**: Reset view

## 🎨 Color Coding

| Color | Meaning | Percentage |
|-------|---------|------------|
| 🔴 Red | High Demand | Top 30% |
| 🟠 Orange | Medium Demand | 30-60% |
| 🟡 Yellow | Moderate Demand | 60-80% |
| 🟢 Green | Lower Demand | Bottom 20% |

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No Skills Data" | Perform a job search first |
| "Network Not Loading" | Refresh page, check console |
| "Sample Data Shown" | Use Enhanced Search for real data |
| "Empty Network" | Lower filter thresholds |

## 💡 Pro Tips

1. **Use Enhanced Search** for better data quality
2. **Try different keywords** for comprehensive analysis
3. **Filter by experience level** for targeted insights
4. **Look for skill clusters** to identify career paths
5. **Check connections** to find complementary skills

## 🎯 Common Use Cases

### For Job Seekers
- Identify skill gaps and learning opportunities
- Plan career transitions based on skill connections
- Understand market demand for your skills

### For Recruiters
- Write better job descriptions based on skill relationships
- Identify essential vs. nice-to-have skills
- Analyze market trends and skill demand

### For Career Development
- Plan skill progression paths
- Identify emerging skills and trends
- Make informed decisions about skill investments

## 📱 Mobile Usage

- **Touch gestures** work for zooming and panning
- **Tap nodes** to highlight connections
- **Swipe** to navigate the network
- **Pinch to zoom** for detailed exploration

## 🔄 Data Sources

- **Real Jobs**: From your actual job searches
- **Sample Data**: Fallback when no real data available
- **Database**: Persistent storage of job data
- **AI Analysis**: Enhanced skill extraction when available

---

**Need Help?** Check the full guide: `SKILLS_NETWORK_USAGE_GUIDE.md`
