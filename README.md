# Yosemite Reservation Monitor

A Flask web application that monitors Yosemite National Park's website for entry reservation requirements and sends email notifications when specific reservation dates are announced.

## Features

- **Intelligent Monitoring**: Automatically scrapes the official Yosemite website for entry reservation announcements
- **Email Notifications**: Sends detailed notifications via SendGrid when specific dates are announced
- **Admin Dashboard**: Secure interface to monitor active requests and manage notifications
- **Privacy Protection**: Email masking in admin interface for user privacy
- **Accurate Detection**: Only notifies for specific announced dates, avoiding false positives

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database
- SendGrid account for email delivery

### Environment Variables

Create a `.env` file with the following variables:

```
DATABASE_URL=postgresql://username:password@host:port/database
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_VERIFIED_SENDER=your_verified_email@domain.com
ADMIN_PASSWORD=your_admin_password
SESSION_SECRET=your_session_secret_key
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/yosemite-reservation-monitor.git
   cd yosemite-reservation-monitor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python main.py
   ```

4. Run the application:
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:5000`.

## Usage

1. **Submit a Monitoring Request**: Visit the homepage and enter your email and desired month
2. **Receive Notifications**: Get email alerts when specific reservation dates are announced
3. **Admin Access**: Visit `/admin-login` to access the dashboard with monitoring statistics

## Technical Details

- **Framework**: Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (production), SQLite (development fallback)
- **Email Service**: SendGrid API
- **Web Scraping**: Trafilatura for content extraction
- **Scheduling**: Automated checks every 30 minutes

## Security

- Session-based admin authentication
- Email address masking in admin interface
- Production-ready security headers
- Environment variable protection for sensitive data

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.