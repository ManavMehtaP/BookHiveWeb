import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
class DataAnalyzer:
    def __init__(self):
        self.events_data = []
        self.users_data = []
        self.bookings_data = []
    def analyze_event_trends(self, events: List[Dict]) -> Dict[str, Any]:
        if not events:
            return {}
        category_counts = {}
        genre_revenue = {}
        for event in events:
            genre = event.get('genre', 'Unknown')
            category_counts[genre] = category_counts.get(genre, 0) + 1
            price = event.get('price', {})
            if isinstance(price, dict):
                amount = price.get('amount', 0)
            else:
                amount = float(price) if price else 0
            genre_revenue[genre] = genre_revenue.get(genre, 0) + amount
        upcoming_events = []
        past_events = []
        for event in events:
            if event.get('is_upcoming', False):
                upcoming_events.append(event)
            else:
                past_events.append(event)
        prices = []
        for event in events:
            price = event.get('price', {})
            if isinstance(price, dict):
                prices.append(price.get('amount', 0))
            else:
                prices.append(float(price) if price else 0)
        avg_price = sum(prices) / len(prices) if prices else 0
        max_price = max(prices) if prices else 0
        min_price = min(prices) if prices else 0
        return {
            'total_events': len(events),
            'category_distribution': category_counts,
            'revenue_by_genre': genre_revenue,
            'upcoming_events': len(upcoming_events),
            'past_events': len(past_events),
            'price_analysis': {
                'average': avg_price,
                'maximum': max_price,
                'minimum': min_price,
                'total_revenue': sum(prices)
            },
            'most_popular_genre': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None,
            'highest_revenue_genre': max(genre_revenue.items(), key=lambda x: x[1])[0] if genre_revenue else None
        }
    def analyze_user_patterns(self, users: List[Dict]) -> Dict[str, Any]:
        if not users:
            return {}
        registration_dates = []
        for user in users:
            created_at = user.get('created_at')
            if created_at:
                registration_dates.append(created_at)
        role_counts = {}
        for user in users:
            role = user.get('role', 'user')
            role_counts[role] = role_counts.get(role, 0) + 1
        return {
            'total_users': len(users),
            'role_distribution': role_counts,
            'registration_trend': self._analyze_time_trend(registration_dates),
            'new_users_this_month': self._count_recent_registrations(registration_dates, 30),
            'new_users_this_week': self._count_recent_registrations(registration_dates, 7)
        }
    def _analyze_time_trend(self, dates: List) -> str:
        if len(dates) < 2:
            return "insufficient_data"
        recent_half = dates[len(dates)//2:]
        older_half = dates[:len(dates)//2]
        if len(recent_half) > len(older_half):
            return "increasing"
        elif len(recent_half) < len(older_half):
            return "decreasing"
        else:
            return "stable"
    def _count_recent_registrations(self, dates: List, days: int) -> int:
        if not dates:
            return 0
        cutoff_date = datetime.now() - timedelta(days=days)
        count = 0
        for date in dates:
            if hasattr(date, 'date'):
                reg_date = date.date()
            else:
                reg_date = date
            if reg_date >= cutoff_date.date():
                count += 1
        return count
    def generate_insights(self, events_analysis: Dict, users_analysis: Dict) -> List[str]:
        insights = []
        if events_analysis.get('total_events', 0) > 0:
            most_popular = events_analysis.get('most_popular_genre')
            if most_popular:
                insights.append(f"Most popular event category: {most_popular}")
            avg_price = events_analysis.get('price_analysis', {}).get('average', 0)
            if avg_price > 0:
                insights.append(f"Average event price: ${avg_price:.2f}")
        if users_analysis.get('total_users', 0) > 0:
            trend = users_analysis.get('registration_trend', 'stable')
            new_monthly = users_analysis.get('new_users_this_month', 0)
            insights.append(f"User registration trend: {trend}")
            if new_monthly > 0:
                insights.append(f"{new_monthly} new users this month")
        return insights
    def export_data_summary(self, events: List[Dict], users: List[Dict]) -> Dict[str, Any]:
        return {
            'export_timestamp': datetime.now().isoformat(),
            'events_summary': self.analyze_event_trends(events),
            'users_summary': self.analyze_user_patterns(users),
            'insights': self.generate_insights(
                self.analyze_event_trends(events),
                self.analyze_user_patterns(users)
            ),
            'data_quality': {
                'total_events_analyzed': len(events),
                'total_users_analyzed': len(users),
                'data_completeness': self._check_data_completeness(events, users)
            }
        }
    def _check_data_completeness(self, events: List[Dict], users: List[Dict]) -> Dict[str, float]:
        total_fields = 0
        completed_fields = 0
        for event in events:
            required_fields = ['title', 'genre', 'location', 'event_date', 'price']
            for field in required_fields:
                total_fields += 1
                if event.get(field) and str(event.get(field)).strip():
                    completed_fields += 1
        for user in users:
            required_fields = ['username', 'email', 'full_name']
            for field in required_fields:
                total_fields += 1
                if user.get(field) and str(user.get(field)).strip():
                    completed_fields += 1
        return {
            'completeness_percentage': (completed_fields / total_fields * 100) if total_fields > 0 else 0,
            'total_fields_checked': total_fields,
            'fields_completed': completed_fields
        }
class ReportGenerator:
    def __init__(self, analyzer: DataAnalyzer):
        self.analyzer = analyzer
    def generate_summary_report(self, events: List[Dict], users: List[Dict]) -> str:
        analysis = self.analyzer.export_data_summary(events, users)
        report = []
        report.append("=" * 60)
        report.append("BOOKHIVE EVENT BOOKING SYSTEM - ANALYTICS REPORT")
        report.append("=" * 60)
        report.append(f"Generated on: {analysis['export_timestamp']}")
        report.append("")
        events_summary = analysis['events_summary']
        report.append("EVENTS SUMMARY:")
        report.append(f"  Total Events: {events_summary['total_events']}")
        report.append(f"  Upcoming Events: {events_summary['upcoming_events']}")
        report.append(f"  Past Events: {events_summary['past_events']}")
        if events_summary.get('most_popular_genre'):
            report.append(f"  Most Popular Category: {events_summary['most_popular_genre']}")
        price_analysis = events_summary.get('price_analysis', {})
        report.append(f"  Average Price: ${price_analysis.get('average', 0):.2f}")
        report.append("")
        users_summary = analysis['users_summary']
        report.append("USERS SUMMARY:")
        report.append(f"  Total Users: {users_summary['total_users']}")
        report.append(f"  New This Month: {users_summary['new_users_this_month']}")
        report.append(f"  Registration Trend: {users_summary['registration_trend']}")
        report.append("")
        report.append("KEY INSIGHTS:")
        for insight in analysis['insights']:
            report.append(f"  • {insight}")
        report.append("=" * 60)
        return "\n".join(report)
    def generate_dashboard_data(self, events: List[Dict], users: List[Dict]) -> Dict[str, Any]:
        events_analysis = self.analyzer.analyze_event_trends(events)
        users_analysis = self.analyzer.analyze_user_patterns(users)
        return {
            'metrics': {
                'total_events': events_analysis['total_events'],
                'total_users': users_analysis['total_users'],
                'upcoming_events': events_analysis['upcoming_events'],
                'new_users_month': users_analysis['new_users_this_month']
            },
            'charts': {
                'category_data': events_analysis['category_distribution'],
                'revenue_data': events_analysis['revenue_by_genre'],
                'user_growth': users_analysis['registration_trend']
            },
            'insights': self.analyzer.generate_insights(events_analysis, users_analysis)
        }
def filter_events_by_criteria(events: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    filtered_events = events.copy()
    if 'genre' in filters:
        genre = filters['genre']
        filtered_events = [e for e in filtered_events if e.get('genre') == genre]
    if 'price_range' in filters:
        min_price, max_price = filters['price_range']
        filtered_events = [
            e for e in filtered_events 
            if min_price <= e.get('price', {}).get('amount', 0) <= max_price
        ]
    if 'date_range' in filters:
        start_date, end_date = filters['date_range']
        filtered_events = [
            e for e in filtered_events 
            if (start_date is None or e.get('event_date') >= start_date) and 
               (end_date is None or e.get('event_date') <= end_date)
        ]
    if 'min_seats' in filters:
        min_seats = filters['min_seats']
        filtered_events = [
            e for e in filtered_events 
            if e.get('seating', {}).get('available', 0) >= min_seats
        ]
    return filtered_events
def sort_events(events: List[Dict], sort_by: str, reverse: bool = False) -> List[Dict]:
    if sort_by == 'date':
        return sorted(events, key=lambda x: x.get('event_date'), reverse=reverse)
    elif sort_by == 'price':
        return sorted(events, key=lambda x: x.get('price', {}).get('amount', 0), reverse=reverse)
    elif sort_by == 'title':
        return sorted(events, key=lambda x: x.get('title', '').lower())
    elif sort_by == 'available_seats':
        return sorted(events, key=lambda x: x.get('seating', {}).get('available', 0), reverse=True)
    else:
        return events
def calculate_booking_statistics(bookings: List[Dict]) -> Dict[str, Any]:
    if not bookings:
        return {
            'total_bookings': 0,
            'active_bookings': 0,
            'cancelled_bookings': 0,
            'total_revenue': 0,
            'average_booking_value': 0
        }
    status_counts = {'active': 0, 'cancelled': 0}
    total_revenue = 0
    for booking in bookings:
        status = booking.get('booking_status', 'active')
        if status in status_counts:
            status_counts[status] += 1
        total_revenue += booking.get('total_price', 0)
    return {
        'total_bookings': len(bookings),
        'status_breakdown': status_counts,
        'total_revenue': total_revenue,
        'average_booking_value': total_revenue / len(bookings) if bookings else 0,
        'booking_rate': (status_counts['active'] / len(bookings) * 100) if bookings else 0
    }