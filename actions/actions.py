import pandas as pd
import random
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import os
from datetime import datetime
import requests

class ActionGiveRecommendation(Action):
    def name(self) -> Text:
        return "action_give_recommendation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            if os.path.exists("data/fashion_comprehensive_dataset_large.csv"):
                df = pd.read_csv("data/fashion_comprehensive_dataset_large.csv")
            else:
                dispatcher.utter_message(text="I'm sorry, I can't access the fashion database right now.")
                return []

            # Get user preferences from slots (including new personalized slots)
            category = tracker.get_slot("clothing_category")
            gender = tracker.get_slot("gender")
            color = tracker.get_slot("color")
            occasion = tracker.get_slot("occasion")
            style = tracker.get_slot("style_preference")
            budget = tracker.get_slot("budget")
            season = tracker.get_slot("season")
            body_type = tracker.get_slot("body_type")
            age_group = tracker.get_slot("age_group")
            weather = tracker.get_slot("weather")
            event = tracker.get_slot("event")
            preference = tracker.get_slot("preference")

            # Check if this is a basic dress request without much context
            last_message = tracker.latest_message.get('text', '').lower()
            is_basic_request = any(word in last_message for word in ['dress', 'dresses', 'top', 'tops', 'pant', 'pants', 'shoe', 'shoes'])
            
            # Check for specific requests like "party dresses", "casual dresses", etc.
            specific_dress_request = False
            dress_type = None
            
            if 'party dress' in last_message or 'party dresses' in last_message:
                specific_dress_request = True
                dress_type = 'party'
            elif 'casual dress' in last_message or 'casual dresses' in last_message:
                specific_dress_request = True
                dress_type = 'casual'
            elif 'formal dress' in last_message or 'formal dresses' in last_message:
                specific_dress_request = True
                dress_type = 'formal'
            elif 'evening dress' in last_message or 'evening dresses' in last_message:
                specific_dress_request = True
                dress_type = 'evening'
            elif 'summer dress' in last_message or 'summer dresses' in last_message:
                specific_dress_request = True
                dress_type = 'summer'
            elif 'cocktail dress' in last_message or 'cocktail dresses' in last_message:
                specific_dress_request = True
                dress_type = 'cocktail'
            elif 'wedding dress' in last_message or 'wedding dresses' in last_message:
                specific_dress_request = True
                dress_type = 'wedding'
            
            # If it's a specific dress request, provide direct recommendations
            if specific_dress_request and dress_type:
                # Filter for the specific dress type
                dress_recommendations = df[df['category'].str.contains('dress', case=False, na=False)]
                dress_recommendations = dress_recommendations[dress_recommendations['occasion'].str.contains(dress_type, case=False, na=False)]
                
                if dress_recommendations.empty:
                    # Fallback to general dress recommendations
                    dress_recommendations = df[df['category'].str.contains('dress', case=False, na=False)]
                
                # Get top 3 recommendations
                recommendations = dress_recommendations.sample(min(3, len(dress_recommendations)))
                
                response = f"🎉 **{dress_type.upper()} DRESS RECOMMENDATIONS** 🎉\n\n"
                response += f"Here are some fabulous {dress_type} dresses perfect for your occasion:\n\n"
                
                for idx, item in recommendations.iterrows():
                    rating = float(item.get('average_rating', 4.0))
                    durability = float(item.get('durability_rating', 3.5))
                    comfort = float(item.get('comfort_rating', 4.0))
                    value_score = (rating + durability + comfort) / 3
                    
                    response += f"**{item['product_name']}** - {item['category'].title()}\n"
                    response += f"🎨 **Style:** {item['pattern']} | **Color:** {item['color']}\n"
                    response += f"⭐ **Value Score:** {value_score:.1f}/5.0 | **Rating:** {rating:.1f}/5.0\n"
                    response += f"💰 **Price:** ${item['price']:.2f} | **Brand:** {item['brand']}\n"
                    response += f"🌍 **Perfect for:** {item['season']} | **Occasion:** {item['occasion']}\n"
                    response += f"🧵 **Material:** {item['material']} | **Fit:** {item.get('fit_type', 'Regular')}\n"
                    response += f"💡 **Styling Tip:** {item.get('styling_tips', 'Pair with complementary accessories for a complete look')}\n\n"
                
                response += f"**💎 {dress_type.upper()} DRESS STYLING TIPS:**\n"
                if dress_type == 'party':
                    response += "• Choose bold colors and eye-catching patterns for party dresses\n"
                    response += "• Accessorize with statement jewelry and elegant heels\n"
                    response += "• Consider the venue lighting when selecting colors\n"
                    response += "• Opt for comfortable fabrics that allow movement\n"
                elif dress_type == 'casual':
                    response += "• Go for breathable, comfortable fabrics for everyday wear\n"
                    response += "• Pair with casual footwear like sneakers or sandals\n"
                    response += "• Choose versatile colors that match your wardrobe\n"
                    response += "• Consider layering options for different weather\n"
                elif dress_type == 'formal':
                    response += "• Select structured, professional cuts for formal occasions\n"
                    response += "• Choose classic colors like navy, black, or neutral tones\n"
                    response += "• Pair with professional accessories and closed-toe shoes\n"
                    response += "• Ensure proper fit and tailoring for a polished look\n"
                elif dress_type == 'evening':
                    response += "• Opt for elegant, sophisticated designs for evening events\n"
                    response += "• Choose rich colors and luxurious fabrics\n"
                    response += "• Accessorize with elegant jewelry and heels\n"
                    response += "• Consider the dress code and venue atmosphere\n"
                elif dress_type == 'summer':
                    response += "• Select lightweight, breathable fabrics for summer comfort\n"
                    response += "• Choose bright, cheerful colors and floral patterns\n"
                    response += "• Pair with sandals or wedges for a summer look\n"
                    response += "• Consider sun protection and ventilation\n"
                elif dress_type == 'cocktail':
                    response += "• Choose sophisticated, semi-formal designs\n"
                    response += "• Opt for classic cuts with modern details\n"
                    response += "• Accessorize with elegant jewelry and heels\n"
                    response += "• Consider the event timing and venue\n"
                elif dress_type == 'wedding':
                    response += "• Select elegant, celebration-appropriate designs\n"
                    response += "• Choose colors that complement the wedding theme\n"
                    response += "• Accessorize with elegant jewelry and formal footwear\n"
                    response += "• Ensure comfort for long celebration periods\n"
                
                response += "\n**🔧 CARE TIPS:**\n"
                response += "• Follow care instructions for longevity\n"
                response += "• Store properly to maintain shape and quality\n"
                response += "• Consider professional cleaning for special occasions\n"
                response += "• Handle with care to preserve delicate details\n\n"
                
                dispatcher.utter_message(text=response)
                return []
            
            # If it's a basic request without context, ask follow-up questions
            if is_basic_request and not (occasion or style or color or budget):
                if 'dress' in last_message or 'dresses' in last_message:
                    response = "👗 **DRESS RECOMMENDATIONS** 👗\n\n"
                    response += "I'd love to help you find the perfect dress! To give you the best recommendations, I need to know:\n\n"
                    response += "**🎯 What type of dress are you looking for?**\n"
                    response += "• Casual dress (everyday wear)\n"
                    response += "• Formal dress (work, business)\n"
                    response += "• Party dress (evening out, celebrations)\n"
                    response += "• Cocktail dress (semi-formal events)\n"
                    response += "• Wedding guest dress\n"
                    response += "• Summer dress\n"
                    response += "• Evening dress\n\n"
                    response += "**🎉 What's the occasion?**\n"
                    response += "• Work/Office\n"
                    response += "• Date night\n"
                    response += "• Party/Celebration\n"
                    response += "• Wedding/Formal event\n"
                    response += "• Casual outing\n"
                    response += "• Travel\n\n"
                    response += "**💰 What's your budget range?**\n"
                    response += "• Budget-friendly ($50-150)\n"
                    response += "• Mid-range ($150-400)\n"
                    response += "• Premium ($400-800)\n"
                    response += "• Luxury ($800+)\n\n"
                    response += "**👤 What's your age group?**\n"
                    response += "• Teens (13-19)\n"
                    response += "• Twenties (20-29)\n"
                    response += "• Thirties (30-39)\n"
                    response += "• Forties (40-49)\n"
                    response += "• Fifties (50-59)\n"
                    response += "• Sixties+ (60+)\n\n"
                    response += "Just tell me what you have in mind! 😊"
                    
                    dispatcher.utter_message(text=response)
                    return []
                
                elif 'top' in last_message or 'tops' in last_message:
                    response = "👕 **TOP RECOMMENDATIONS** 👕\n\n"
                    response += "Great choice! Let me help you find the perfect top. I need to know:\n\n"
                    response += "**🎯 What type of top?**\n"
                    response += "• Blouse (elegant, work-appropriate)\n"
                    response += "• T-shirt (casual, comfortable)\n"
                    response += "• Tank top (summer, casual)\n"
                    response += "• Sweater (winter, cozy)\n"
                    response += "• Crop top (trendy, party)\n"
                    response += "• Button-down shirt (professional)\n\n"
                    response += "**🎉 What's the occasion?**\n"
                    response += "• Work/Office\n"
                    response += "• Casual day out\n"
                    response += "• Party/Evening\n"
                    response += "• Date night\n"
                    response += "• Weekend brunch\n\n"
                    response += "**💰 Budget range?**\n"
                    response += "• Budget-friendly ($20-80)\n"
                    response += "• Mid-range ($80-200)\n"
                    response += "• Premium ($200-500)\n"
                    response += "• Luxury ($500+)\n\n"
                    response += "**👤 What's your age group?**\n"
                    response += "• Teens (13-19)\n"
                    response += "• Twenties (20-29)\n"
                    response += "• Thirties (30-39)\n"
                    response += "• Forties (40-49)\n"
                    response += "• Fifties (50-59)\n"
                    response += "• Sixties+ (60+)\n\n"
                    response += "Tell me what you're looking for! ✨"
                    
                    dispatcher.utter_message(text=response)
                    return []
                
                elif 'pant' in last_message or 'pants' in last_message:
                    response = "👖 **PANTS RECOMMENDATIONS** 👖\n\n"
                    response += "Perfect! Let me find you the ideal pants. I need to know:\n\n"
                    response += "**🎯 What type of pants?**\n"
                    response += "• Jeans (casual, versatile)\n"
                    response += "• Dress pants (professional)\n"
                    response += "• Leggings (comfortable, active)\n"
                    response += "• Wide-leg pants (trendy, elegant)\n"
                    response += "• Skinny pants (slim fit)\n"
                    response += "• Palazzo pants (flowy, summer)\n\n"
                    response += "**🎉 What's the occasion?**\n"
                    response += "• Work/Office\n"
                    response += "• Casual day\n"
                    response += "• Evening out\n"
                    response += "• Weekend\n"
                    response += "• Travel\n\n"
                    response += "**💰 Budget range?**\n"
                    response += "• Budget-friendly ($30-120)\n"
                    response += "• Mid-range ($120-300)\n"
                    response += "• Premium ($300-600)\n"
                    response += "• Luxury ($600+)\n\n"
                    response += "**👤 What's your age group?**\n"
                    response += "• Teens (13-19)\n"
                    response += "• Twenties (20-29)\n"
                    response += "• Thirties (30-39)\n"
                    response += "• Forties (40-49)\n"
                    response += "• Fifties (50-59)\n"
                    response += "• Sixties+ (60+)\n\n"
                    response += "What do you have in mind? 🎯"
                    
                    dispatcher.utter_message(text=response)
                    return []
                
                elif 'shoe' in last_message or 'shoes' in last_message:
                    response = "👟 **SHOES RECOMMENDATIONS** 👟\n\n"
                    response += "Excellent! Let me help you find the perfect shoes. I need to know:\n\n"
                    response += "**🎯 What type of shoes?**\n"
                    response += "• Sneakers (casual, comfortable)\n"
                    response += "• Heels (elegant, formal)\n"
                    response += "• Flats (comfortable, versatile)\n"
                    response += "• Boots (winter, stylish)\n"
                    response += "• Sandals (summer, breezy)\n"
                    response += "• Loafers (professional, classic)\n\n"
                    response += "**🎉 What's the occasion?**\n"
                    response += "• Work/Office\n"
                    response += "• Casual day\n"
                    response += "• Party/Evening\n"
                    response += "• Date night\n"
                    response += "• Travel/Walking\n\n"
                    response += "**💰 Budget range?**\n"
                    response += "• Budget-friendly ($50-150)\n"
                    response += "• Mid-range ($150-300)\n"
                    response += "• Premium ($300-600)\n"
                    response += "• Luxury ($600+)\n\n"
                    response += "**👤 What's your age group?**\n"
                    response += "• Teens (13-19)\n"
                    response += "• Twenties (20-29)\n"
                    response += "• Thirties (30-39)\n"
                    response += "• Forties (40-49)\n"
                    response += "• Fifties (50-59)\n"
                    response += "• Sixties+ (60+)\n\n"
                    response += "What are you looking for? 👠"
                    
                    dispatcher.utter_message(text=response)
                    return []

            # Build personalized recommendation message
            personalization = []
            if body_type:
                personalization.append(f"body type ({body_type})")
            if age_group:
                personalization.append(f"age group ({age_group})")
            if weather:
                personalization.append(f"weather ({weather})")
            if event:
                personalization.append(f"event ({event})")
            if preference:
                personalization.append(f"preference ({preference})")

            # Filter data based on preferences
            filtered_df = df.copy()
            
            if category:
                filtered_df = filtered_df[filtered_df['category'].str.contains(category, case=False, na=False)]
            
            if gender:
                filtered_df = filtered_df[filtered_df['gender'].str.contains(gender, case=False, na=False)]
            
            if color:
                filtered_df = filtered_df[filtered_df['color'].str.contains(color, case=False, na=False)]
            
            if occasion:
                filtered_df = filtered_df[filtered_df['occasion'].str.contains(occasion, case=False, na=False)]
            
            if style:
                filtered_df = filtered_df[filtered_df['style_preference'].str.contains(style, case=False, na=False)]
            
            if budget:
                # Enhanced budget filtering
                try:
                    price_series = pd.to_numeric(filtered_df['price'], errors='coerce')
                    if 'budget-friendly' in budget.lower() or 'low' in budget.lower():
                        filtered_df = filtered_df[price_series <= 150]
                    elif 'mid-range' in budget.lower() or 'medium' in budget.lower():
                        filtered_df = filtered_df[(price_series > 150) & (price_series <= 400)]
                    elif 'premium' in budget.lower():
                        filtered_df = filtered_df[(price_series > 400) & (price_series <= 800)]
                    elif 'luxury' in budget.lower() or 'high' in budget.lower():
                        filtered_df = filtered_df[price_series > 800]
                    else:
                        # Fallback to string matching
                        filtered_df = filtered_df[filtered_df['price'].astype(str).str.contains(budget, case=False, na=False)]
                except:
                    # Fallback to original string matching
                    filtered_df = filtered_df[filtered_df['price'].astype(str).str.contains(budget, case=False, na=False)]
            
            if season:
                filtered_df = filtered_df[filtered_df['Season'].str.contains(season, case=False, na=False)]

            # Personalized recommendations based on body type
            if body_type:
                body_type_recommendations = self.get_body_type_recommendations(body_type, filtered_df)
                if body_type_recommendations:
                    filtered_df = body_type_recommendations

            # Age-appropriate recommendations
            if age_group:
                age_recommendations = self.get_age_recommendations(age_group, filtered_df)
                if age_recommendations:
                    filtered_df = age_recommendations

            # Weather-appropriate recommendations
            if weather:
                weather_recommendations = self.get_weather_recommendations(weather, filtered_df)
                if weather_recommendations:
                    filtered_df = weather_recommendations

            if filtered_df.empty:
                dispatcher.utter_message(text="I couldn't find any items matching your preferences. Let me suggest some general recommendations.")
                # Get random recommendations
                recommendations = df.sample(min(3, len(df)))
            else:
                recommendations = filtered_df.sample(min(3, len(filtered_df)))

            # Build enhanced personalized response
            if personalization:
                response = f"🎯 **PERSONALIZED FASHION RECOMMENDATIONS** 🎯\n\n"
                response += f"Based on your {', '.join(personalization)}, here are your perfect fashion matches:\n\n"
            else:
                response = "🎯 **FASHION RECOMMENDATIONS** 🎯\n\n"
                response += "Here are some amazing fashion recommendations for you:\n\n"
            
            for idx, item in recommendations.iterrows():
                # Calculate value score
                rating = float(item.get('average_rating', 4.0))
                durability = float(item.get('durability_rating', 3.5))
                comfort = float(item.get('comfort_rating', 4.0))
                value_score = (rating + durability + comfort) / 3
                
                response += f"**{item['product_name']}** - {item['category'].title()}\n"
                response += f"🎨 **Style:** {item['pattern']} | **Color:** {item['color']}\n"
                response += f"⭐ **Value Score:** {value_score:.1f}/5.0 | **Rating:** {rating:.1f}/5.0\n"
                response += f"💰 **Price:** ${item['price']:.2f} | **Brand:** {item['brand']}\n"
                response += f"🌍 **Perfect for:** {item['season']} | **Occasion:** {item['occasion']}\n"
                response += f"🧵 **Material:** {item['material']} | **Fit:** {item.get('fit_type', 'Regular')}\n"
                response += f"💡 **Styling Tip:** {item.get('styling_tips', 'Pair with complementary accessories for a complete look')}\n\n"

            # Add comprehensive styling insights
            response += "**💎 STYLING INSIGHTS:**\n"
            response += "• These items are carefully selected to match your preferences\n"
            response += "• Each piece offers excellent value for money\n"
            response += "• Versatile enough to create multiple outfit combinations\n"
            response += "• Perfect for your lifestyle and occasion needs\n\n"

            # Add personalized styling tips
            if body_type or age_group or preference:
                styling_tip = self.get_personalized_styling_tip(body_type, age_group, preference)
                response += f"**💡 PERSONALIZED STYLING TIP:**\n{styling_tip}\n\n"

            # Add quality and care information
            response += "**🔧 QUALITY & CARE:**\n"
            response += "• Follow care instructions for longevity\n"
            response += "• Invest in proper storage solutions\n"
            response += "• Consider professional alterations for perfect fit\n"
            response += "• Regular maintenance extends garment life\n\n"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"I encountered an error while processing your request: {str(e)}")

        return []

    def get_body_type_recommendations(self, body_type: str, df: pd.DataFrame) -> pd.DataFrame:
        """Get recommendations based on body type"""
        body_type_tips = {
            'hourglass': ['fitted', 'wrap', 'belted', 'structured'],
            'petite': ['high-waisted', 'monochrome', 'vertical', 'fitted'],
            'plus size': ['structured', 'v-neck', 'dark', 'fitted'],
            'rectangular': ['layered', 'textured', 'belted', 'fitted'],
            'tall': ['layered', 'horizontal', 'textured', 'fitted'],
            'slim': ['layered', 'textured', 'loose', 'patterned'],
            'curves': ['v-neck', 'structured', 'fitted', 'dark'],
            'athletic': ['fitted', 'structured', 'textured', 'layered'],
            'apple': ['v-neck', 'dark', 'structured', 'fitted'],
            'pear': ['v-neck', 'structured', 'fitted', 'dark'],
            'inverted triangle': ['v-neck', 'loose', 'dark', 'textured'],
            'diamond': ['v-neck', 'structured', 'fitted', 'dark'],
            'oval': ['v-neck', 'structured', 'fitted', 'dark'],
            'triangle': ['v-neck', 'structured', 'fitted', 'dark'],
            'rectangle': ['layered', 'textured', 'belted', 'fitted'],
            'curvy': ['v-neck', 'structured', 'fitted', 'dark'],
            'short': ['high-waisted', 'monochrome', 'vertical', 'fitted'],
            'medium': ['fitted', 'structured', 'textured', 'layered']
        }
        
        if body_type.lower() in body_type_tips:
            tips = body_type_tips[body_type.lower()]
            filtered = df[df['pattern'].str.contains('|'.join(tips), case=False, na=False)]
            return filtered if not filtered.empty else df
        return df

    def get_age_recommendations(self, age_group: str, df: pd.DataFrame) -> pd.DataFrame:
        """Get age-appropriate recommendations"""
        age_appropriate_styles = {
            'teens': ['trendy', 'casual', 'fun', 'colorful'],
            'twenties': ['trendy', 'casual', 'sophisticated', 'fun'],
            'thirties': ['sophisticated', 'classic', 'trendy', 'professional'],
            'forties': ['sophisticated', 'classic', 'elegant', 'professional'],
            'fifties': ['classic', 'elegant', 'sophisticated', 'comfortable'],
            'sixties': ['classic', 'elegant', 'comfortable', 'sophisticated'],
            'young': ['trendy', 'casual', 'fun', 'colorful'],
            'middle aged': ['sophisticated', 'classic', 'elegant', 'professional'],
            'senior': ['classic', 'elegant', 'comfortable', 'sophisticated'],
            'teenager': ['trendy', 'casual', 'fun', 'colorful'],
            'young adult': ['trendy', 'sophisticated', 'casual', 'professional'],
            'professional': ['sophisticated', 'classic', 'elegant', 'professional'],
            'student': ['trendy', 'casual', 'fun', 'affordable'],
            'parent': ['comfortable', 'practical', 'sophisticated', 'classic'],
            'grandparent': ['classic', 'elegant', 'comfortable', 'sophisticated']
        }
        
        if age_group.lower() in age_appropriate_styles:
            styles = age_appropriate_styles[age_group.lower()]
            filtered = df[df['pattern'].str.contains('|'.join(styles), case=False, na=False)]
            return filtered if not filtered.empty else df
        return df

    def get_weather_recommendations(self, weather: str, df: pd.DataFrame) -> pd.DataFrame:
        """Get weather-appropriate recommendations"""
        weather_appropriate = {
            'sunny': ['light', 'breathable', 'summer', 'casual'],
            'rainy': ['waterproof', 'layered', 'warm', 'practical'],
            'cold': ['warm', 'layered', 'winter', 'cozy'],
            'hot': ['light', 'breathable', 'summer', 'casual'],
            'warm': ['light', 'breathable', 'spring', 'casual'],
            'cloudy': ['layered', 'versatile', 'casual', 'comfortable'],
            'snowing': ['warm', 'layered', 'winter', 'cozy'],
            'windy': ['layered', 'structured', 'practical', 'comfortable'],
            'humid': ['light', 'breathable', 'casual', 'comfortable'],
            'dry': ['light', 'breathable', 'casual', 'comfortable'],
            'mild': ['versatile', 'layered', 'casual', 'comfortable'],
            'chilly': ['warm', 'layered', 'comfortable', 'cozy'],
            'freezing': ['warm', 'layered', 'winter', 'cozy'],
            'scorching': ['light', 'breathable', 'summer', 'casual'],
            'pleasant': ['versatile', 'casual', 'comfortable', 'elegant']
        }
        
        if weather.lower() in weather_appropriate:
            styles = weather_appropriate[weather.lower()]
            filtered = df[df['pattern'].str.contains('|'.join(styles), case=False, na=False)]
            return filtered if not filtered.empty else df
        return df

    def get_personalized_styling_tip(self, body_type: str, age_group: str, preference: str) -> str:
        """Get personalized styling tips"""
        tips = []
        
        if body_type:
            body_tips = {
                'hourglass': 'Embrace your curves with fitted silhouettes and belted pieces.',
                'petite': 'Opt for high-waisted items and monochrome looks to create length.',
                'plus size': 'Choose structured pieces and dark colors for a flattering look.',
                'rectangular': 'Add definition with layered pieces and textured fabrics.',
                'tall': 'Experiment with horizontal lines and layered looks.',
                'slim': 'Add volume with layered pieces and textured fabrics.',
                'curves': 'Highlight your waist with fitted pieces and v-neck styles.',
                'athletic': 'Embrace fitted silhouettes and structured pieces.',
                'apple': 'Draw attention upward with v-neck styles and structured pieces.',
                'pear': 'Balance your proportions with v-neck tops and structured pieces.',
                'inverted triangle': 'Add volume to your lower half with textured fabrics.',
                'diamond': 'Create definition with structured pieces and v-neck styles.',
                'oval': 'Add structure with fitted pieces and v-neck styles.',
                'triangle': 'Balance with v-neck styles and structured pieces.',
                'rectangle': 'Create curves with layered pieces and belted styles.',
                'curvy': 'Embrace your shape with fitted pieces and v-neck styles.',
                'short': 'Create length with high-waisted items and vertical lines.',
                'medium': 'Experiment with different silhouettes and layered looks.'
            }
            if body_type.lower() in body_tips:
                tips.append(body_tips[body_type.lower()])
        
        if age_group:
            age_tips = {
                'teens': 'Have fun with trends while staying comfortable and age-appropriate.',
                'twenties': 'Mix trendy pieces with classic staples for a balanced wardrobe.',
                'thirties': 'Invest in quality pieces that reflect your growing sophistication.',
                'forties': 'Focus on elegant, well-fitted pieces that make you feel confident.',
                'fifties': 'Choose classic styles with modern touches for timeless elegance.',
                'sixties': 'Prioritize comfort and elegance with well-crafted pieces.',
                'young': 'Experiment with trends while building a foundation of classics.',
                'middle aged': 'Balance sophistication with comfort in your style choices.',
                'senior': 'Choose elegant, comfortable pieces that reflect your confidence.',
                'professional': 'Build a wardrobe of sophisticated, versatile pieces.',
                'student': 'Mix affordable trends with practical, comfortable pieces.',
                'parent': 'Choose practical, comfortable pieces that still make you feel stylish.',
                'grandparent': 'Embrace elegant, comfortable styles that reflect your wisdom.'
            }
            if age_group.lower() in age_tips:
                tips.append(age_tips[age_group.lower()])
        
        if preference:
            preference_tips = {
                'comfortable': 'Prioritize comfort without sacrificing style with stretch fabrics and relaxed fits.',
                'stylish': 'Focus on well-fitted pieces and current trends that suit your personality.',
                'elegant': 'Choose sophisticated pieces with clean lines and quality fabrics.',
                'casual': 'Build a wardrobe of comfortable, versatile pieces for everyday wear.',
                'sophisticated': 'Invest in quality pieces with refined details and classic silhouettes.',
                'trendy': 'Stay current with fashion trends while maintaining your personal style.',
                'modest': 'Choose pieces with appropriate coverage while staying stylish.',
                'bold': 'Embrace vibrant colors and statement pieces that express your personality.',
                'neutral': 'Build a cohesive wardrobe with neutral tones and versatile pieces.',
                'loose': 'Choose relaxed fits that provide comfort and a modern silhouette.',
                'fitted': 'Opt for well-tailored pieces that flatter your figure.',
                'oversized': 'Embrace the relaxed trend with intentionally oversized pieces.',
                'minimalist': 'Focus on clean lines, quality fabrics, and essential pieces.',
                'detailed': 'Choose pieces with interesting details and textures.',
                'simple': 'Keep your style clean and uncomplicated with essential pieces.'
            }
            if preference.lower() in preference_tips:
                tips.append(preference_tips[preference.lower()])
        
        if tips:
            return ' '.join(tips)
        else:
            return "Focus on pieces that make you feel confident and comfortable."

class ActionTrendingItems(Action):
    def name(self) -> Text:
        return "action_trending_items"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            if os.path.exists("data/fashion_comprehensive_dataset_large.csv"):
                df = pd.read_csv("data/fashion_comprehensive_dataset_large.csv")
            else:
                dispatcher.utter_message(text="I'm sorry, I can't access the fashion database right now.")
                return []

            # Get trending items with enhanced analysis
            trending_items = df.sample(min(5, len(df)))
            
            response = "🔥 **TRENDING FASHION ITEMS** 🔥\n\n"
            response += "Here are the hottest fashion items trending right now:\n\n"
            
            for idx, item in trending_items.iterrows():
                # Calculate trend score based on ratings and trend level
                try:
                    trend_score = float(item.get('trend_level', 3.5))
                except (ValueError, TypeError):
                    trend_score = 3.5
                try:
                    rating = float(item.get('average_rating', 4.0))
                except (ValueError, TypeError):
                    rating = 4.0
                overall_score = (trend_score + rating) / 2
                
                response += f"**{item['product_name']}** - {item['category'].title()}\n"
                response += f"🎨 **Style:** {item['pattern']} | **Color:** {item['color']}\n"
                response += f"⭐ **Trend Score:** {overall_score:.1f}/5.0 | **Rating:** {rating:.1f}/5.0\n"
                response += f"💰 **Price:** ${item['price']:.2f} | **Brand:** {item['brand']}\n"
                response += f"🌍 **Perfect for:** {item['season']} | **Occasion:** {item['occasion']}\n"
                response += f"💡 **Styling Tip:** {item.get('styling_tips', 'Pair with complementary accessories for a complete look')}\n\n"

            response += "**💎 TREND INSIGHTS:**\n"
            response += "• These items are currently dominating social media and fashion blogs\n"
            response += "• Perfect for creating Instagram-worthy outfits\n"
            response += "• Great investment pieces for your wardrobe\n"
            response += "• Versatile enough to style multiple ways\n\n"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"I encountered an error while processing your request: {str(e)}")

        return []

class ActionOutfitCombination(Action):
    def name(self) -> Text:
        return "action_outfit_combination"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        try:
            if os.path.exists("data/fashion_comprehensive_dataset_large.csv"):
                df = pd.read_csv("data/fashion_comprehensive_dataset_large.csv")
            else:
                dispatcher.utter_message(text="I'm sorry, I can't access the fashion database right now.")
                return []

            # Get enhanced outfit combinations
            tops = df[df['category'].str.contains('shirt|blouse|top', case=False, na=False)].sample(min(2, len(df)))
            bottoms = df[df['category'].str.contains('jeans|shorts|skirt|pants', case=False, na=False)].sample(min(2, len(df)))
            shoes = df[df['category'].str.contains('shoes|boots|sneakers', case=False, na=False)].sample(min(2, len(df)))

            response = "👗 **STYLISH OUTFIT COMBINATIONS** 👗\n\n"
            response += "Here are some expertly curated outfit combinations for you:\n\n"
            
            for i in range(min(len(tops), len(bottoms), len(shoes))):
                # Calculate style score for each outfit
                try:
                    top_rating = float(tops.iloc[i].get('average_rating', 4.0))
                except (ValueError, TypeError):
                    top_rating = 4.0
                try:
                    bottom_rating = float(bottoms.iloc[i].get('average_rating', 4.0))
                except (ValueError, TypeError):
                    bottom_rating = 4.0
                try:
                    shoe_rating = float(shoes.iloc[i].get('average_rating', 4.0))
                except (ValueError, TypeError):
                    shoe_rating = 4.0
                outfit_score = (top_rating + bottom_rating + shoe_rating) / 3
                
                response += f"**Outfit {i+1}** - Style Score: {outfit_score:.1f}/5.0 ⭐\n"
                response += f"👕 **Top:** {tops.iloc[i]['product_name']} ({tops.iloc[i]['color']})\n"
                response += f"   Brand: {tops.iloc[i]['brand']} | Price: ${tops.iloc[i]['price']:.2f}\n"
                response += f"👖 **Bottom:** {bottoms.iloc[i]['product_name']} ({bottoms.iloc[i]['color']})\n"
                response += f"   Brand: {bottoms.iloc[i]['brand']} | Price: ${bottoms.iloc[i]['price']:.2f}\n"
                response += f"👟 **Shoes:** {shoes.iloc[i]['product_name']} ({shoes.iloc[i]['color']})\n"
                response += f"   Brand: {shoes.iloc[i]['brand']} | Price: ${shoes.iloc[i]['price']:.2f}\n"
                response += f"💡 **Styling Tip:** {tops.iloc[i].get('styling_tips', 'Perfect for a casual yet stylish look')}\n\n"

            response += "**💎 OUTFIT COORDINATION TIPS:**\n"
            response += "• Mix textures for visual interest\n"
            response += "• Balance proportions for flattering silhouettes\n"
            response += "• Coordinate colors for harmonious looks\n"
            response += "• Add accessories to complete the ensemble\n"
            response += "• Consider the occasion when styling\n\n"

            response += "**🔧 QUALITY & VERSATILITY:**\n"
            response += "• Each piece is versatile and can be mixed with other items\n"
            response += "• High-quality materials ensure longevity\n"
            response += "• Comfortable fit for all-day wear\n"
            response += "• Easy to care for and maintain\n\n"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"I encountered an error while processing your request: {str(e)}")

        return []

class ActionStyleAdvice(Action):
    def name(self) -> Text:
        return "action_style_advice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get personalized information from slots
        body_type = tracker.get_slot("body_type")
        age_group = tracker.get_slot("age_group")
        preference = tracker.get_slot("preference")
        gender = tracker.get_slot("gender")
        
        # Build personalized advice
        advice_parts = []
        
        # Body type specific advice
        if body_type:
            body_advice = self.get_body_type_advice(body_type)
            advice_parts.append(body_advice)
        
        # Age-specific advice
        if age_group:
            age_advice = self.get_age_advice(age_group)
            advice_parts.append(age_advice)
        
        # Preference-based advice
        if preference:
            preference_advice = self.get_preference_advice(preference)
            advice_parts.append(preference_advice)
        
        # General style tips
        general_tips = [
            "Mix and match different textures for a more interesting look.",
            "Don't be afraid to experiment with bold colors and patterns.",
            "Invest in quality basics that you can wear multiple ways.",
            "Accessorize to elevate any outfit - jewelry, scarves, or belts.",
            "Layer pieces for a more sophisticated and versatile wardrobe.",
            "Keep your color palette cohesive for easy mixing and matching.",
            "Don't forget about fit - well-fitted clothes always look better.",
            "Experiment with different styles to find what makes you feel confident.",
            "Remember that confidence is the best accessory you can wear.",
            "Build a capsule wardrobe with versatile pieces that mix and match easily.",
            "Pay attention to proportions when creating outfits.",
            "Use color psychology to express your mood and personality.",
            "Invest in timeless pieces that never go out of style.",
            "Don't be afraid to break fashion rules - style is personal!",
            "Take care of your clothes to make them last longer and look better."
        ]
        
        if advice_parts:
            personalized_advice = " ".join(advice_parts)
            general_tip = random.choice(general_tips)
            full_advice = f"{personalized_advice} {general_tip}"
        else:
            full_advice = random.choice(general_tips)
        
        dispatcher.utter_message(text=f"Here's personalized style advice for you: {full_advice}")
        
        return []

    def get_body_type_advice(self, body_type: str) -> str:
        """Get body type specific advice"""
        body_advice = {
            'hourglass': "For your hourglass figure, emphasize your waist with fitted pieces and belted styles. Wrap dresses and high-waisted bottoms will flatter your curves beautifully.",
            'petite': "As a petite person, opt for high-waisted items and monochrome looks to create length. Avoid overwhelming prints and choose fitted silhouettes.",
            'plus size': "Choose structured pieces and dark colors for a flattering look. V-neck styles and well-fitted clothing will highlight your best features.",
            'rectangular': "Add definition with layered pieces and textured fabrics. Belts and structured pieces will help create curves and shape.",
            'tall': "Experiment with horizontal lines and layered looks. You can pull off bold patterns and oversized pieces beautifully.",
            'slim': "Add volume with layered pieces and textured fabrics. Don't be afraid to experiment with different silhouettes and patterns.",
            'curves': "Highlight your waist with fitted pieces and v-neck styles. Structured pieces will help define your shape elegantly.",
            'athletic': "Embrace fitted silhouettes and structured pieces. You can rock tailored looks and add softness with flowy pieces.",
            'apple': "Draw attention upward with v-neck styles and structured pieces. Choose darker colors for the midsection and lighter colors up top.",
            'pear': "Balance your proportions with v-neck tops and structured pieces. Choose darker colors for bottoms and lighter colors for tops.",
            'inverted triangle': "Add volume to your lower half with textured fabrics and patterns. Choose structured pieces for the upper body.",
            'diamond': "Create definition with structured pieces and v-neck styles. Focus on highlighting your waist and shoulders.",
            'oval': "Add structure with fitted pieces and v-neck styles. Choose pieces that create definition and shape.",
            'triangle': "Balance with v-neck styles and structured pieces. Add volume to your upper half with interesting details.",
            'rectangle': "Create curves with layered pieces and belted styles. Add definition with structured pieces and interesting textures.",
            'curvy': "Embrace your shape with fitted pieces and v-neck styles. Choose structured pieces that highlight your curves beautifully.",
            'short': "Create length with high-waisted items and vertical lines. Choose fitted silhouettes and avoid overwhelming pieces.",
            'medium': "Experiment with different silhouettes and layered looks. You have the flexibility to try various styles and trends."
        }
        return body_advice.get(body_type.lower(), "Focus on pieces that make you feel confident and comfortable.")

    def get_age_advice(self, age_group: str) -> str:
        """Get age-specific advice"""
        age_advice = {
            'teens': "Have fun with trends while staying comfortable and age-appropriate. Experiment with colors and styles to find your personal style.",
            'twenties': "Mix trendy pieces with classic staples for a balanced wardrobe. Invest in quality basics that will last.",
            'thirties': "Invest in quality pieces that reflect your growing sophistication. Build a wardrobe that's both professional and stylish.",
            'forties': "Focus on elegant, well-fitted pieces that make you feel confident. Choose timeless styles with modern touches.",
            'fifties': "Choose classic styles with modern touches for timeless elegance. Prioritize comfort without sacrificing style.",
            'sixties': "Prioritize comfort and elegance with well-crafted pieces. Choose sophisticated styles that reflect your confidence.",
            'young': "Experiment with trends while building a foundation of classics. Don't be afraid to try new styles.",
            'middle aged': "Balance sophistication with comfort in your style choices. Choose pieces that reflect your experience and confidence.",
            'senior': "Choose elegant, comfortable pieces that reflect your confidence. Focus on quality and timeless style.",
            'professional': "Build a wardrobe of sophisticated, versatile pieces. Choose items that work for both office and casual settings.",
            'student': "Mix affordable trends with practical, comfortable pieces. Focus on versatile items that work for various occasions.",
            'parent': "Choose practical, comfortable pieces that still make you feel stylish. Look for easy-care fabrics and versatile styles.",
            'grandparent': "Embrace elegant, comfortable styles that reflect your wisdom. Choose pieces that make you feel confident and beautiful."
        }
        return age_advice.get(age_group.lower(), "Choose pieces that reflect your personality and make you feel confident.")

    def get_preference_advice(self, preference: str) -> str:
        """Get preference-based advice"""
        preference_advice = {
            'comfortable': "Prioritize comfort without sacrificing style. Look for stretch fabrics, relaxed fits, and breathable materials.",
            'stylish': "Focus on well-fitted pieces and current trends that suit your personality. Don't be afraid to make bold choices.",
            'elegant': "Choose sophisticated pieces with clean lines and quality fabrics. Focus on timeless styles and refined details.",
            'casual': "Build a wardrobe of comfortable, versatile pieces for everyday wear. Choose items that are easy to mix and match.",
            'sophisticated': "Invest in quality pieces with refined details and classic silhouettes. Focus on understated elegance.",
            'trendy': "Stay current with fashion trends while maintaining your personal style. Mix trendy pieces with classic staples.",
            'modest': "Choose pieces with appropriate coverage while staying stylish. Look for elegant, sophisticated styles.",
            'bold': "Embrace vibrant colors and statement pieces that express your personality. Don't be afraid to stand out.",
            'neutral': "Build a cohesive wardrobe with neutral tones and versatile pieces. Focus on mix-and-match potential.",
            'loose': "Choose relaxed fits that provide comfort and a modern silhouette. Embrace the oversized trend thoughtfully.",
            'fitted': "Opt for well-tailored pieces that flatter your figure. Focus on proper fit and structured silhouettes.",
            'oversized': "Embrace the relaxed trend with intentionally oversized pieces. Balance with fitted items for proportion.",
            'minimalist': "Focus on clean lines, quality fabrics, and essential pieces. Keep your wardrobe simple and versatile.",
            'detailed': "Choose pieces with interesting details and textures. Look for unique elements that add personality.",
            'simple': "Keep your style clean and uncomplicated with essential pieces. Focus on quality over quantity."
        }
        return preference_advice.get(preference.lower(), "Choose pieces that align with your personal style preferences.")

class ActionSizeGuide(Action):
    def name(self) -> Text:
        return "action_size_guide"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        gender = tracker.get_slot("gender")
        
        if gender and gender.lower() in ['women', 'female', 'woman']:
            size_guide = """
Women's Size Guide:
• XS: 0-2 (Bust: 32-33", Waist: 24-25", Hips: 34-35")
• S: 4-6 (Bust: 34-35", Waist: 26-27", Hips: 36-37")
• M: 8-10 (Bust: 36-37", Waist: 28-29", Hips: 38-39")
• L: 12-14 (Bust: 38-39", Waist: 30-31", Hips: 40-41")
• XL: 16-18 (Bust: 40-41", Waist: 32-33", Hips: 42-43")
• XXL: 20-22 (Bust: 42-43", Waist: 34-35", Hips: 44-45")
            """
        elif gender and gender.lower() in ['men', 'male', 'man']:
            size_guide = """
Men's Size Guide:
• XS: 30-32 (Chest: 30-32", Waist: 26-28", Neck: 14-14.5")
• S: 34-36 (Chest: 34-36", Waist: 30-32", Neck: 15-15.5")
• M: 38-40 (Chest: 38-40", Waist: 34-36", Neck: 16-16.5")
• L: 42-44 (Chest: 42-44", Waist: 38-40", Neck: 17-17.5")
• XL: 46-48 (Chest: 46-48", Waist: 42-44", Neck: 18-18.5")
• XXL: 50-52 (Chest: 50-52", Waist: 46-48", Neck: 19-19.5")
            """
        else:
            size_guide = """
General Size Guide:
• XS: Extra Small
• S: Small
• M: Medium
• L: Large
• XL: Extra Large
• XXL: Extra Extra Large

For accurate sizing, always check the specific brand's size chart as sizes can vary between brands.
            """
        
        dispatcher.utter_message(text=size_guide)
        return []

class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Simple fallback response
        fallback_responses = [
            "I'm still learning about fashion! Could you be more specific about what you're looking for?",
            "I didn't quite catch that. Can you try asking in a different way?",
            "I'm here to help with fashion advice! Try asking about recommendations, trends, or style tips.",
            "Let me help you with fashion! You can ask me about clothing recommendations, trending items, or style advice."
        ]
        
        response = random.choice(fallback_responses)
        dispatcher.utter_message(text=response)
        
        return []

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Default fallback response
        fallback_responses = [
            "I'm sorry, I didn't understand that. Can you try asking about fashion recommendations, style advice, or trending items?",
            "I'm here to help with fashion! Try asking me about clothing, style tips, or outfit combinations.",
            "I didn't catch that. You can ask me about fashion advice, recommendations, or trending styles.",
            "Let me help you with fashion! Ask me about clothes, style, or fashion trends."
        ]
        
        response = random.choice(fallback_responses)
        dispatcher.utter_message(text=response)
        
        return []
