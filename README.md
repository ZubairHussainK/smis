# 🏫 SMIS - School Management Information System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

A comprehensive School Management Information System built with PyQt5, featuring modern UI design, security features, and complete educational administration tools.

## 🌟 Features

### 📚 Academic Management
- **Student Management:** Complete student records with photos, academic history
- **Teacher Management:** Staff profiles, qualifications, assignments
- **Attendance Tracking:** Daily attendance with reports and analytics
- **Class Management:** Grade levels, sections, subject assignments

### 📊 Reports & Analytics
- **Academic Reports:** Performance tracking, grade reports
- **Attendance Reports:** Daily, monthly, yearly attendance statistics
- **Custom Reports:** Flexible reporting with date ranges
- **Data Export:** PDF and Excel export capabilities

### 🔐 Security Features
- **User Authentication:** Secure login with role-based access
- **Data Encryption:** Encrypted sensitive data storage
- **Audit Logging:** Complete activity tracking
- **Backup System:** Automated database backups

### 🎨 Modern UI/UX
- **Professional Design:** Clean, intuitive interface
- **Responsive Layout:** Adaptive design for different screen sizes
- **Dark/Light Themes:** User preference theme switching
- **Material Icons:** Modern iconography throughout

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PyQt5 5.15+
- SQLite3 (included with Python)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ZubairHussainK/smis.git
cd smis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

### Default Login
- **Username:** `admin`
- **Password:** `admin123`

## 📁 Project Structure

```
SMIS/
├── 📂 core/                    # Core application modules
│   ├── auth.py                 # Authentication system
│   ├── security_manager.py     # Security features
│   └── database.py             # Database management
├── 📂 ui/                      # User interface modules
│   ├── pages/                  # Application pages
│   │   ├── student.py          # Student management
│   │   ├── attendance.py       # Attendance tracking
│   │   ├── reports.py          # Reports generation
│   │   ├── settings.py         # Application settings
│   │   ├── student_list.py     # Student listing
│   │   └── mother_reg.py       # Mother registration
│   └── styles/                 # UI styling
│       └── table_styles.py     # Centralized table styling
├── 📂 models/                  # Data models
│   └── database.py             # Database schema
├── 📂 services/                # Business logic services
│   ├── backup_service.py       # Backup automation
│   └── notification_service.py # Notifications
├── 📂 resources/               # Static resources
│   ├── icons/                  # Application icons
│   ├── images/                 # Images and logos
│   └── styles/                 # CSS stylesheets
├── 📂 config/                  # Configuration files
└── main.py                     # Application entry point
```

## 🛠️ Development

### Setting up Development Environment

1. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install development dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure VS Code (Optional):**
   - The project includes `.vscode/settings.json` for optimal development experience
   - Pylance type checking configured for PyQt5 compatibility

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Maintain consistent naming conventions
- Add docstrings for public methods

## 🔧 Configuration

### Database Setup
The application uses SQLite by default. Database file is created automatically on first run.

### Environment Variables
Create a `.env` file in the root directory:
```env
DB_PATH=school.db
LOG_LEVEL=INFO
BACKUP_INTERVAL=24
THEME=light
```

### Security Configuration
- Encryption keys are auto-generated
- Default admin credentials should be changed after first login
- Regular backup schedule recommended

## 📊 Database Schema

### Main Tables
- **students:** Student information and academic records
- **teachers:** Staff profiles and assignments
- **attendance:** Daily attendance tracking
- **classes:** Grade levels and sections
- **subjects:** Academic subjects
- **users:** System users and authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Update documentation for API changes
- Follow existing code style
- Add appropriate error handling

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

**Q: Application won't start**
A: Ensure Python 3.8+ and PyQt5 are properly installed

**Q: Database errors**
A: Check write permissions in application directory

**Q: Login issues**
A: Use default credentials: admin/admin123

### Getting Help
- 📧 Email: support@smis.edu
- 🐛 Issues: [GitHub Issues](https://github.com/ZubairHussainK/smis/issues)
- 📖 Documentation: [Wiki](https://github.com/ZubairHussainK/smis/wiki)

## 🏆 Acknowledgments

- PyQt5 team for the excellent GUI framework
- SQLite team for the reliable database engine
- Material Design for UI inspiration
- Contributors and testers

## 📈 Roadmap

### Version 2.1 (Planned)
- [ ] Web interface
- [ ] Mobile app companion
- [ ] Advanced analytics
- [ ] Integration with external systems

### Version 2.2 (Future)
- [ ] Multi-school support
- [ ] Cloud deployment
- [ ] API development
- [ ] Real-time notifications

---

<div align="center">

**Built with ❤️ for Education**

[![GitHub Stars](https://img.shields.io/github/stars/ZubairHussainK/smis.svg?style=social&label=Star)](https://github.com/ZubairHussainK/smis/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ZubairHussainK/smis.svg?style=social&label=Fork)](https://github.com/ZubairHussainK/smis/network/members)

</div>
