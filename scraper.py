import trafilatura
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

def check_yosemite_availability(month):
    """
    Check Yosemite entry reservation requirements for a given month
    Returns a tuple of (bool, list) where bool indicates if reservations are required
    and list contains the dates requiring reservations
    """
    try:
        # Updated URL to the main Yosemite page where reservation info would be posted
        url = "https://www.nps.gov/yose/planyourvisit/reservations.htm"
        downloaded = trafilatura.fetch_url(url)
        content = trafilatura.extract(downloaded)

        logger.info(f"Checking entry reservation requirements for {month}")
        reservation_dates = []

        if not content:
            logger.error("Failed to fetch content from Yosemite website")
            return False, []

        # Convert month to lowercase for case-insensitive comparison
        month_lower = month.lower()
        content_lower = content.lower()

        # Log the content for debugging
        logger.debug(f"Retrieved content: {content[:500]}...")  # First 500 chars for debugging

        # Enhanced regular expressions to find date ranges for the specified month
        # Patterns to match various date formats:
        # - "February 8–9" 
        # - "February 15–17"
        # - "February 8-9" (with regular dash)
        # - "February 8–9, February 15–17"
        # - "February 8–9, February 15–17, and February 22–23"
        
        patterns = [
            # Single date range: "February 8–9"
            rf"{month}\s+\d+(?:[–-]\d+)?",
            # Multiple date ranges: "February 8–9, February 15–17, and February 22–23"
            rf"{month}\s+\d+(?:[–-]\d+)?(?:,\s+{month}\s+\d+(?:[–-]\d+)?)*(?:,?\s+and\s+{month}\s+\d+(?:[–-]\d+)?)?",
            # Year-specific patterns: "February 8–9, 2025"
            rf"{month}\s+\d+(?:[–-]\d+)?,?\s+\d{{4}}",
        ]

        found_dates = False
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                found_dates = True
                date_range = match.group(0).strip()
                # Only add if not already in the list
                if date_range not in reservation_dates:
                    reservation_dates.append(date_range)
                    logger.info(f"Found date range requiring reservation: {date_range}")

        # Additional validation: ensure we're actually finding reservation-related content
        if found_dates:
            # Look for context words around the dates to confirm they're about reservations
            context_keywords = ['reservation', 'require', 'entry', 'timed', 'permit', 'advance']
            has_reservation_context = any(keyword in content_lower for keyword in context_keywords)
            
            if not has_reservation_context:
                logger.warning(f"Found dates for {month} but no reservation context detected. Skipping notification.")
                found_dates = False
                reservation_dates = []

        # Only return True if we found specific dates
        if found_dates:
            logger.info(f"Found specific reservation dates for {month}: {reservation_dates}")
            return True, reservation_dates

        logger.info(f"No specific reservation dates found for {month}")
        return False, []
    except Exception as e:
        logger.error(f"Error checking reservation requirements: {str(e)}")
        return False, []