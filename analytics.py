import json
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from database import get_db_connection, save_analytics_event, get_analytics_data

def track_resume_view(resume_id: int, viewer_info: dict = None):
    """Track when a resume is viewed"""
    try:
        event_data = {
            'timestamp': datetime.now().isoformat(),
            'viewer_ip': viewer_info.get('ip', 'unknown') if viewer_info else 'unknown',
            'user_agent': viewer_info.get('user_agent', 'unknown') if viewer_info else 'unknown'
        }
        
        save_analytics_event(resume_id, 'view', event_data)
        
    except Exception as e:
        st.error(f"Failed to track resume view: {str(e)}")

def track_resume_download(resume_id: int, format_type: str, user_info: dict = None):
    """Track when a resume is downloaded"""
    try:
        event_data = {
            'format': format_type,
            'timestamp': datetime.now().isoformat(),
            'user_info': user_info or {}
        }
        
        save_analytics_event(resume_id, 'download', event_data)
        
    except Exception as e:
        st.error(f"Failed to track resume download: {str(e)}")

def track_resume_share(resume_id: int, share_type: str, recipient_info: dict = None):
    """Track when a resume is shared"""
    try:
        event_data = {
            'share_type': share_type,
            'timestamp': datetime.now().isoformat(),
            'recipient_info': recipient_info or {}
        }
        
        save_analytics_event(resume_id, 'share', event_data)
        
    except Exception as e:
        st.error(f"Failed to track resume share: {str(e)}")

def track_job_application(resume_id: int, job_info: dict):
    """Track when resume is used for job application"""
    try:
        event_data = {
            'company': job_info.get('company', ''),
            'position': job_info.get('position', ''),
            'application_date': datetime.now().isoformat(),
            'job_board': job_info.get('source', 'unknown'),
            'status': 'applied'
        }
        
        save_analytics_event(resume_id, 'job_application', event_data)
        
    except Exception as e:
        st.error(f"Failed to track job application: {str(e)}")

def get_resume_analytics(resume_id: int) -> dict:
    """Get comprehensive analytics for a resume"""
    try:
        # Get basic analytics from database
        analytics_data = get_analytics_data(resume_id)
        
        # Enhance with additional calculations
        enhanced_analytics = analytics_data.copy()
        
        # Calculate engagement metrics
        enhanced_analytics.update({
            'engagement_score': _calculate_engagement_score(analytics_data),
            'performance_trend': _analyze_performance_trend(resume_id),
            'top_referrers': _get_top_referrers(resume_id),
            'geographic_data': _get_geographic_insights(resume_id),
            'device_breakdown': _get_device_breakdown(resume_id),
            'time_analytics': _get_time_based_analytics(resume_id)
        })
        
        return enhanced_analytics
        
    except Exception as e:
        st.error(f"Failed to get resume analytics: {str(e)}")
        return {}

def _calculate_engagement_score(analytics_data: dict) -> float:
    """Calculate engagement score based on various metrics"""
    try:
        views = analytics_data.get('total_views', 0)
        downloads = analytics_data.get('downloads', 0)
        shares = analytics_data.get('shares', 0)
        
        if views == 0:
            return 0.0
        
        # Calculate engagement rates
        download_rate = downloads / views if views > 0 else 0
        share_rate = shares / views if views > 0 else 0
        
        # Weight different actions
        engagement_score = (
            views * 1.0 +
            downloads * 5.0 +
            shares * 3.0
        ) / max(1, views)
        
        # Normalize to 0-100 scale
        return min(100, engagement_score * 10)
        
    except:
        return 0.0

def _analyze_performance_trend(resume_id: int) -> dict:
    """Analyze performance trends over time"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get data for last 30 days
        cursor.execute("""
            SELECT DATE(created_at) as date, event_type, COUNT(*) as count
            FROM resume_analytics 
            WHERE resume_id = %s 
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(created_at), event_type
            ORDER BY date DESC
        """, (resume_id,))
        
        results = cursor.fetchall()
        
        # Process trend data
        trend_data = {}
        for row in results:
            date_str = str(row[0])
            event_type = row[1]
            count = row[2]
            
            if date_str not in trend_data:
                trend_data[date_str] = {}
            trend_data[date_str][event_type] = count
        
        # Calculate trend direction
        dates = sorted(trend_data.keys())
        if len(dates) >= 7:
            recent_week = dates[-7:]
            previous_week = dates[-14:-7] if len(dates) >= 14 else []
            
            recent_total = sum(sum(trend_data[d].values()) for d in recent_week)
            previous_total = sum(sum(trend_data[d].values()) for d in previous_week) if previous_week else recent_total
            
            trend_direction = "up" if recent_total > previous_total else "down" if recent_total < previous_total else "stable"
        else:
            trend_direction = "insufficient_data"
        
        return {
            'trend_direction': trend_direction,
            'daily_data': trend_data,
            'data_points': len(dates)
        }
        
    except Exception as e:
        return {'trend_direction': 'error', 'daily_data': {}, 'data_points': 0}
    finally:
        if conn:
            conn.close()

def _get_top_referrers(resume_id: int) -> list:
    """Get top referrer sources"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_data->>'referrer' as referrer, COUNT(*) as count
            FROM resume_analytics 
            WHERE resume_id = %s 
            AND event_type = 'view'
            AND event_data->>'referrer' IS NOT NULL
            GROUP BY event_data->>'referrer'
            ORDER BY count DESC
            LIMIT 10
        """, (resume_id,))
        
        results = cursor.fetchall()
        return [{'source': row[0], 'count': row[1]} for row in results]
        
    except Exception as e:
        return []
    finally:
        if conn:
            conn.close()

def _get_geographic_insights(resume_id: int) -> dict:
    """Get geographic insights from view data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_data->>'location' as location, COUNT(*) as count
            FROM resume_analytics 
            WHERE resume_id = %s 
            AND event_type = 'view'
            AND event_data->>'location' IS NOT NULL
            GROUP BY event_data->>'location'
            ORDER BY count DESC
            LIMIT 20
        """, (resume_id,))
        
        results = cursor.fetchall()
        locations = [{'location': row[0], 'views': row[1]} for row in results]
        
        return {
            'top_locations': locations,
            'total_locations': len(locations),
            'geographic_diversity': len(locations) / max(1, sum(loc['views'] for loc in locations))
        }
        
    except Exception as e:
        return {'top_locations': [], 'total_locations': 0, 'geographic_diversity': 0}
    finally:
        if conn:
            conn.close()

def _get_device_breakdown(resume_id: int) -> dict:
    """Get device/browser breakdown"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT event_data->>'user_agent' as user_agent, COUNT(*) as count
            FROM resume_analytics 
            WHERE resume_id = %s 
            AND event_type = 'view'
            AND event_data->>'user_agent' IS NOT NULL
            GROUP BY event_data->>'user_agent'
            ORDER BY count DESC
        """, (resume_id,))
        
        results = cursor.fetchall()
        
        # Simple device detection
        mobile_count = 0
        desktop_count = 0
        tablet_count = 0
        
        for row in results:
            user_agent = row[0].lower()
            count = row[1]
            
            if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
                mobile_count += count
            elif 'tablet' in user_agent or 'ipad' in user_agent:
                tablet_count += count
            else:
                desktop_count += count
        
        total = mobile_count + desktop_count + tablet_count
        
        return {
            'mobile': {'count': mobile_count, 'percentage': (mobile_count / max(1, total)) * 100},
            'desktop': {'count': desktop_count, 'percentage': (desktop_count / max(1, total)) * 100},
            'tablet': {'count': tablet_count, 'percentage': (tablet_count / max(1, total)) * 100}
        }
        
    except Exception as e:
        return {
            'mobile': {'count': 0, 'percentage': 0},
            'desktop': {'count': 0, 'percentage': 0},
            'tablet': {'count': 0, 'percentage': 0}
        }
    finally:
        if conn:
            conn.close()

def _get_time_based_analytics(resume_id: int) -> dict:
    """Get time-based analytics (hourly, daily patterns)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get hourly distribution
        cursor.execute("""
            SELECT EXTRACT(HOUR FROM created_at) as hour, COUNT(*) as count
            FROM resume_analytics 
            WHERE resume_id = %s 
            AND event_type = 'view'
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY EXTRACT(HOUR FROM created_at)
            ORDER BY hour
        """, (resume_id,))
        
        hourly_results = cursor.fetchall()
        hourly_data = {int(row[0]): row[1] for row in hourly_results}
        
        # Get daily distribution (day of week)
        cursor.execute("""
            SELECT EXTRACT(DOW FROM created_at) as dow, COUNT(*) as count
            FROM resume_analytics 
            WHERE resume_id = %s 
            AND event_type = 'view'
            AND created_at >= NOW() - INTERVAL '30 days'
            GROUP BY EXTRACT(DOW FROM created_at)
            ORDER BY dow
        """, (resume_id,))
        
        daily_results = cursor.fetchall()
        
        # Map day of week numbers to names
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        daily_data = {day_names[int(row[0])]: row[1] for row in daily_results}
        
        # Find peak hours and days
        peak_hour = max(hourly_data, key=hourly_data.get) if hourly_data else 0
        peak_day = max(daily_data, key=daily_data.get) if daily_data else "Unknown"
        
        return {
            'hourly_distribution': hourly_data,
            'daily_distribution': daily_data,
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'business_hours_percentage': _calculate_business_hours_percentage(hourly_data)
        }
        
    except Exception as e:
        return {
            'hourly_distribution': {},
            'daily_distribution': {},
            'peak_hour': 0,
            'peak_day': 'Unknown',
            'business_hours_percentage': 0
        }
    finally:
        if conn:
            conn.close()

def _calculate_business_hours_percentage(hourly_data: dict) -> float:
    """Calculate percentage of views during business hours (9 AM - 5 PM)"""
    if not hourly_data:
        return 0.0
    
    business_hours_views = sum(count for hour, count in hourly_data.items() if 9 <= hour <= 17)
    total_views = sum(hourly_data.values())
    
    return (business_hours_views / max(1, total_views)) * 100

def generate_analytics_report(user_id: int, date_range: int = 30) -> dict:
    """Generate comprehensive analytics report for user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's resumes
        cursor.execute("""
            SELECT id, title FROM resumes WHERE user_id = %s
        """, (user_id,))
        
        resumes = cursor.fetchall()
        
        report = {
            'user_id': user_id,
            'report_date': datetime.now().isoformat(),
            'date_range_days': date_range,
            'total_resumes': len(resumes),
            'resume_analytics': {},
            'summary_stats': {},
            'insights': []
        }
        
        total_views = 0
        total_downloads = 0
        total_shares = 0
        
        # Get analytics for each resume
        for resume_id, title in resumes:
            analytics = get_resume_analytics(resume_id)
            report['resume_analytics'][title] = analytics
            
            total_views += analytics.get('total_views', 0)
            total_downloads += analytics.get('downloads', 0)
            total_shares += analytics.get('shares', 0)
        
        # Calculate summary statistics
        report['summary_stats'] = {
            'total_views': total_views,
            'total_downloads': total_downloads,
            'total_shares': total_shares,
            'average_engagement': total_downloads / max(1, total_views) * 100,
            'most_viewed_resume': _get_most_viewed_resume(report['resume_analytics']),
            'performance_trend': _calculate_overall_trend(user_id, date_range)
        }
        
        # Generate insights
        report['insights'] = _generate_insights(report)
        
        return report
        
    except Exception as e:
        st.error(f"Failed to generate analytics report: {str(e)}")
        return {}
    finally:
        if conn:
            conn.close()

def _get_most_viewed_resume(resume_analytics: dict) -> str:
    """Find the most viewed resume"""
    if not resume_analytics:
        return "None"
    
    max_views = 0
    most_viewed = "None"
    
    for title, analytics in resume_analytics.items():
        views = analytics.get('total_views', 0)
        if views > max_views:
            max_views = views
            most_viewed = title
    
    return most_viewed

def _calculate_overall_trend(user_id: int, date_range: int) -> str:
    """Calculate overall performance trend"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent activity
        cursor.execute("""
            SELECT DATE(ra.created_at) as date, COUNT(*) as count
            FROM resume_analytics ra
            JOIN resumes r ON ra.resume_id = r.id
            WHERE r.user_id = %s 
            AND ra.created_at >= NOW() - INTERVAL '%s days'
            GROUP BY DATE(ra.created_at)
            ORDER BY date
        """, (user_id, date_range))
        
        results = cursor.fetchall()
        
        if len(results) < 7:
            return "insufficient_data"
        
        # Compare first half with second half
        mid_point = len(results) // 2
        first_half_total = sum(row[1] for row in results[:mid_point])
        second_half_total = sum(row[1] for row in results[mid_point:])
        
        if second_half_total > first_half_total * 1.1:
            return "improving"
        elif second_half_total < first_half_total * 0.9:
            return "declining"
        else:
            return "stable"
            
    except Exception as e:
        return "error"
    finally:
        if conn:
            conn.close()

def _generate_insights(report: dict) -> list:
    """Generate actionable insights from analytics data"""
    insights = []
    
    summary = report.get('summary_stats', {})
    total_views = summary.get('total_views', 0)
    engagement = summary.get('average_engagement', 0)
    trend = summary.get('performance_trend', 'unknown')
    
    # View-based insights
    if total_views == 0:
        insights.append("📊 Your resumes haven't been viewed yet. Consider sharing them on professional networks.")
    elif total_views < 10:
        insights.append("🚀 You're getting started! Share your resume more widely to increase visibility.")
    elif total_views > 100:
        insights.append("🎉 Great visibility! Your resumes are getting good exposure.")
    
    # Engagement insights
    if engagement < 5:
        insights.append("📈 Low engagement rate. Consider updating your resume content to be more compelling.")
    elif engagement > 20:
        insights.append("💼 Excellent engagement! Your resume content is resonating well with viewers.")
    
    # Trend insights
    if trend == "improving":
        insights.append("📈 Your resume performance is trending upward! Keep up the good work.")
    elif trend == "declining":
        insights.append("📉 Performance is declining. Consider refreshing your resume or sharing it in new places.")
    elif trend == "stable":
        insights.append("📊 Steady performance. Consider trying new strategies to boost visibility.")
    
    # Resume-specific insights
    resume_analytics = report.get('resume_analytics', {})
    if len(resume_analytics) > 1:
        view_counts = {title: data.get('total_views', 0) for title, data in resume_analytics.items()}
        best_performer = max(view_counts, key=view_counts.get) if view_counts else None
        
        if best_performer and view_counts[best_performer] > 0:
            insights.append(f"🏆 '{best_performer}' is your top-performing resume. Consider using its format for others.")
    
    return insights

def export_analytics_data(user_id: int, format_type: str = 'csv') -> bytes:
    """Export analytics data in various formats"""
    try:
        # Generate comprehensive report
        report = generate_analytics_report(user_id)
        
        if format_type.lower() == 'csv':
            return _export_to_csv(report)
        elif format_type.lower() == 'json':
            return json.dumps(report, indent=2).encode('utf-8')
        else:
            return b""
            
    except Exception as e:
        st.error(f"Analytics export failed: {str(e)}")
        return b""

def _export_to_csv(report: dict) -> bytes:
    """Export analytics report to CSV format"""
    try:
        import io
        
        output = io.StringIO()
        
        # Write summary
        output.write("TAC Resume Builder - Analytics Report\n")
        output.write(f"Generated: {report.get('report_date', 'Unknown')}\n")
        output.write(f"Date Range: {report.get('date_range_days', 0)} days\n\n")
        
        # Write summary stats
        summary = report.get('summary_stats', {})
        output.write("Summary Statistics\n")
        output.write("Metric,Value\n")
        for key, value in summary.items():
            output.write(f"{key},{value}\n")
        
        output.write("\nResume Performance\n")
        output.write("Resume,Views,Downloads,Shares,Engagement Score\n")
        
        # Write resume data
        for title, analytics in report.get('resume_analytics', {}).items():
            views = analytics.get('total_views', 0)
            downloads = analytics.get('downloads', 0)
            shares = analytics.get('shares', 0)
            engagement = analytics.get('engagement_score', 0)
            
            output.write(f'"{title}",{views},{downloads},{shares},{engagement:.1f}\n')
        
        return output.getvalue().encode('utf-8')
        
    except Exception as e:
        return b""

