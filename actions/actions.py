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
            if os.path.exists("data/fashion_data_cleaned.csv"):
                df = pd.read_csv("data/fashion_data_cleaned.csv")
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

            # Build personalized response
            if personalization:
                response = f"Based on your {', '.join(personalization)}, here are personalized fashion recommendations:\n\n"
            else:
                response = "Here are some fashion recommendations for you:\n\n"
            
            for idx, item in recommendations.iterrows():
                response += f"• {item['product_name']} - {item['category']} ({item['color']})\n"
                response += f"  Style: {item['pattern']} | Price: ${item['price']:.2f}\n"
                response += f"  Perfect for: {item['season']}\n\n"

            # Add personalized styling tips
            if body_type or age_group or preference:
                styling_tip = self.get_personalized_styling_tip(body_type, age_group, preference)
                response += f"💡 **Personalized Styling Tip:** {styling_tip}\n\n"

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
            if os.path.exists("data/fashion_data_cleaned.csv"):
                df = pd.read_csv("data/fashion_data_cleaned.csv")
            else:
                dispatcher.utter_message(text="I'm sorry, I can't access the fashion database right now.")
                return []

            # Get trending items (random selection for demo)
            trending_items = df.sample(min(5, len(df)))
            
            response = "Here are the trending fashion items right now:\n\n"
            
            for idx, item in trending_items.iterrows():
                response += f"🔥 {item['product_name']} - {item['category']}\n"
                response += f"   Style: {item['pattern']} | Color: {item['color']}\n"
                response += f"   Perfect for: {item['season']}\n\n"

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
            if os.path.exists("data/fashion_data_cleaned.csv"):
                df = pd.read_csv("data/fashion_data_cleaned.csv")
            else:
                dispatcher.utter_message(text="I'm sorry, I can't access the fashion database right now.")
                return []

            # Get outfit combinations
            tops = df[df['category'].str.contains('shirt|blouse', case=False, na=False)].sample(min(2, len(df)))
            bottoms = df[df['category'].str.contains('jeans|shorts|skirt', case=False, na=False)].sample(min(2, len(df)))
            shoes = df[df['category'].str.contains('shoes', case=False, na=False)].sample(min(2, len(df)))

            response = "Here are some stylish outfit combinations:\n\n"
            
            for i in range(min(len(tops), len(bottoms), len(shoes))):
                response += f"Outfit {i+1}:\n"
                response += f"👕 {tops.iloc[i]['product_name']} ({tops.iloc[i]['color']})\n"
                response += f"👖 {bottoms.iloc[i]['product_name']} ({bottoms.iloc[i]['color']})\n"
                response += f"👟 {shoes.iloc[i]['product_name']} ({shoes.iloc[i]['color']})\n\n"

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
