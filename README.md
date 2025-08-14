# Trade Analytics Dashboard

Interactive visualization of US trade relationships and tariff data using Dash and Plotly.

## 🔒 Security Notice

**IMPORTANT**: This app does NOT contain any API keys or sensitive data. All configuration is handled through environment variables.

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd trade-analytics
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional)
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

5. **Access the app**
   - Open http://localhost:8050 in your browser

### Production Deployment

#### Render.com (Recommended)

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Configure the service:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:server`
   - **Environment Variables**: Add any needed variables in Render dashboard

4. **Deploy**
   - Render will automatically deploy when you push to your main branch

#### Other Platforms

- **Heroku**: Use the included `Procfile`
- **Railway**: Use the same configuration as Render
- **DigitalOcean App Platform**: Use the same configuration as Render

## 📁 Project Structure

```
trade-analytics/
├── app.py                 # Main Dash application
├── app_advanced.py        # Advanced version (backup)
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment
├── Dockerfile            # Docker deployment
├── .gitignore            # Git ignore rules
├── env.example           # Environment variables template
├── Tariff.csv            # Trade data
├── usa_map_PNG2.png      # US map background
└── README.md             # This file
```

## 🔧 Configuration

The app uses environment variables for configuration:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `False` | Enable debug mode |
| `PORT` | `8050` | Port to run the app on |
| `HOST` | `0.0.0.0` | Host to bind to |
| `CSV_PATH` | `Tariff.csv` | Path to trade data CSV |
| `SECRET_KEY` | `your-secret-key...` | Flask secret key |

## 📊 Features

- **Interactive Trade Network Visualization**
  - Rectangular layout showing US trade relationships
  - Sortable by deficit, exports, imports, or tariff percentage
  - Toggleable trade flow lines
  - Hover information for each country

- **Data Sources**
  - US trade deficit data
  - Export/import statistics
  - Tariff information
  - Country-specific metrics

## 🛠️ Development

### Adding New Features

1. **Data**: Add new columns to `Tariff.csv`
2. **Visualization**: Modify `build_figure()` function in `app.py`
3. **Interactivity**: Add new callbacks in `app.py`

### Testing

```bash
# Run the app in debug mode
DEBUG=True python app.py
```

## 🔒 Security Checklist

Before deploying, ensure:

- [ ] No API keys in code (use environment variables)
- [ ] `.env` file is in `.gitignore`
- [ ] No sensitive data in repository
- [ ] CORS properly configured
- [ ] Debug mode disabled in production

## 📝 License

This project is for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions, please create an issue in the repository.


