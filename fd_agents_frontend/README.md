# 🎯 FD Portfolio Optimizer - Frontend

Beautiful, responsive web interface for the FD Portfolio Optimizer project.

## 📋 Features

✅ **Interactive Form**
- Slider and number input for investment amount (Rs 1L to Rs 10L)
- Tenure selection (6, 12, 18, 24 months)
- Risk profile chooser (Conservative, Moderate, Aggressive)

✅ **Real-time Results**
- Summary cards showing investment, returns, interest, and maturity amount
- Detailed allocation table across 8 banks
- Interest calculations for each bank
- Bank-wise maturity amounts

✅ **AI Recommendations**
- Agent 1: Bank Selection Guidance (which banks fit your timeline)
- Agent 2: Rate Decision (Book Now / Wait / Flexible)
- Confidence levels and market analysis

✅ **Professional UI**
- Responsive design (desktop, tablet, mobile)
- Modern gradient colors
- Smooth animations and transitions
- Loading spinner during API calls
- Error handling with retry option

## 🚀 Quick Start

### Step 1: Start the Backend API
```bash
cd c:\Users\Saika Khan\Downloads\AI\fd_agents
python api_new.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 2: Start the Frontend Server
```bash
cd c:\Users\Saika Khan\Downloads\AI\fd_agents_frontend
python server.py
```

Expected output:
```
✅ Server running on: http://localhost:3000
✅ Open in browser: http://localhost:3000
```

### Step 3: Open in Browser
Visit: **http://localhost:3000**

## 📁 Project Structure

```
fd_agents_frontend/
├── index.html       # Main HTML structure
├── style.css        # Styling and layout
├── script.js        # JavaScript for API integration
├── server.py        # Simple Python HTTP server
└── README.md        # This file
```

## 🔧 Configuration

To change the backend API URL, edit `script.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000'; // Change this if needed
```

## 📱 Responsive Design

The interface works on:
- 🖥️ Desktop (1200px+)
- 💻 Tablet (768px - 1024px)
- 📱 Mobile (< 768px)

## 🎨 Colors Used

- Primary Blue: `#2563eb`
- Success Green: `#10b981`
- Warning Orange: `#f59e0b`
- Text Gray: `#1f2937`

## 🔌 API Integration

Frontend calls:

**POST /optimize**
```json
{
  "amount": 1000000,
  "tenure": 12,
  "risk": "moderate"
}
```

**Response:**
```json
{
  "success": true,
  "report": "... full portfolio report ...",
  "timestamp": "2026-04-19T01:08:38.563090",
  "request_params": {...},
  "error": null
}
```

## 🐛 Troubleshooting

**Issue:** "Connection Error: Unable to reach backend"
- Solution: Make sure `python api_new.py` is running on port 8000

**Issue:** Page shows blank
- Solution: Check browser console (F12) for errors
- Verify server is running: `python server.py`

**Issue:** Styles not loading
- Solution: Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

## 📚 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🚦 Running Both Servers

**Terminal 1 - Backend API:**
```bash
cd fd_agents
python api_new.py
```

**Terminal 2 - Frontend Server:**
```bash
cd fd_agents_frontend
python server.py
```

Then open: http://localhost:3000

## 📊 What You Can Do

1. **Adjust Investment Amount** - Use slider or number input
2. **Choose Tenure** - 6, 12, 18, or 24 months
3. **Select Risk Profile** - Conservative, Moderate, or Aggressive
4. **Get Results** - Click "Optimize My Portfolio"
5. **Review Recommendations** - See PSO allocation + AI insights
6. **Take Action** - Follow the "Key Actions" section

## 🔐 Security

- All API calls use HTTPS-ready code
- Form inputs are validated
- No sensitive data stored locally
- Backend API runs on localhost only

## 📞 Support

If you encounter issues:
1. Check backend is running: `python api_new.py`
2. Check frontend is running: `python server.py`
3. Check both are on correct ports (8000 and 3000)
4. Check browser console for errors (F12)

---

**Happy Investing!** 💰🎯
