# Chatbot Web Scraping Integration Guide

## Overview

The ChroniSense AI Health Coach chatbot has been enhanced with web scraping capabilities to provide more comprehensive, evidence-based health information. The chatbot now enriches its responses with curated medical knowledge from reliable health sources.

---

## Features Added

### 1. Web Scraper Service (`app/services/web_scraper.py`)

A new service that provides:

- **Health Topic Knowledge**: Scrapes/provides information on common health topics
- **Health Tips Database**: Condition-specific and category-based health tips
- **Normal Ranges**: Reference ranges for vital signs and health metrics
- **Caching**: Efficient caching of scraped content to reduce redundant requests

#### Key Methods:

```python
# Get information about a health topic
knowledge = scraper.scrape_health_topic('hypertension', max_length=500)

# Get health tips by condition and category
tips = scraper.search_health_tips('hypertension', 'diet')

# Get normal ranges for vital signs
ranges = scraper.get_normal_ranges('blood_pressure')
```

### 2. Enhanced Chatbot (`app/services/chatbot.py`)

The chatbot now:

- Integrates web-scraped knowledge into responses
- Provides more detailed, evidence-based health information
- Personalizes scraped content with patient vitals
- Offers condition-specific health tips

#### Example Enhancement:

**Before (Rule-based):**
```
"Given your blood pressure readings, try to limit processed foods."
```

**After (Web-enhanced):**
```
"Based on current medical guidelines: Blood pressure is measured in millimeters 
of mercury (mmHg)... Your current blood pressure is 145/90. This is elevated. 
Please follow the recommendations above and consult your healthcare provider."
```

### 3. New API Endpoints

#### `/api/health-tips/<patient_id>`
Get personalized health tips for a patient based on their condition.

**Request:**
```http
GET /api/health-tips/1?category=diet
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "tips": [
    "Reduce sodium intake to less than 2,300mg per day",
    "Eat more potassium-rich foods like bananas, spinach, and sweet potatoes",
    "Follow the DASH diet with plenty of fruits, vegetables, and whole grains"
  ],
  "category": "diet"
}
```

#### `/api/web-knowledge`
Get web-scraped health knowledge about any topic.

**Request:**
```http
GET /api/web-knowledge?topic=hypertension&max_length=500
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "topic": "hypertension",
  "knowledge": "High blood pressure (hypertension) is a common condition..."
}
```

---

## Health Topics Covered

The web scraper provides curated information on:

1. **Hypertension / Blood Pressure**
   - Causes, symptoms, and management
   - Normal ranges and stages
   - Lifestyle modifications

2. **Diabetes**
   - Blood sugar management
   - Dietary recommendations
   - Monitoring guidelines

3. **Diet & Nutrition**
   - Heart-healthy eating
   - DASH diet principles
   - Sodium reduction strategies

4. **Exercise & Activity**
   - Physical activity guidelines
   - Benefits for chronic conditions
   - Starting safely

5. **Stress Management**
   - Impact on health
   - Relaxation techniques
   - Lifestyle strategies

6. **Medication Adherence**
   - Importance of compliance
   - Tips for remembering medications
   - Side effect management

7. **Sleep**
   - Sleep requirements
   - Impact on cardiovascular health
   - Sleep hygiene tips

8. **Weight Management**
   - Healthy weight ranges
   - Sustainable strategies
   - Benefits for chronic conditions

---

## Usage Examples

### In Chat Interface

**User asks:** "What can I do about my high blood pressure?"

**Chatbot response:**
```
Based on current medical guidelines: High blood pressure (hypertension) is a 
common condition where the force of blood against artery walls is too high. 
Managing hypertension involves lifestyle changes like reducing sodium intake, 
exercising regularly, maintaining healthy weight, limiting alcohol, and 
managing stress. Medications may also be prescribed.

Your current blood pressure is 145/90. This is elevated. Please follow the 
recommendations above and consult your healthcare provider.
```

### Getting Health Tips

**User asks:** "What should I eat today?"

**Chatbot checks patient condition** (e.g., hypertension) **and provides:**
```
For better management of your condition, here are some dietary recommendations:

1. Reduce sodium intake to less than 2,300mg per day
2. Eat more potassium-rich foods like bananas, spinach, and sweet potatoes
3. Follow the DASH diet with plenty of fruits, vegetables, and whole grains
4. Limit alcohol consumption to moderate levels
5. Reduce saturated and trans fats in your diet

Remember to consult with your healthcare provider for personalized dietary advice.
```

---

## Knowledge Base Coverage

### Condition-Specific Tips

#### Hypertension
- **Diet**: Sodium reduction, DASH diet, potassium-rich foods
- **Exercise**: Aerobic activity, strength training, monitoring guidelines
- **Lifestyle**: Weight management, stress reduction, sleep optimization

#### Diabetes
- **Diet**: Carbohydrate management, portion control, meal timing
- **Exercise**: Blood sugar effects, safety precautions, activity types
- **Monitoring**: Testing schedules, pattern recognition, A1C tracking

#### General Wellness
- Hydration, balanced nutrition, physical activity, stress management

### Vital Sign Ranges

#### Blood Pressure
- Normal: < 120/80 mmHg
- Elevated: 120-129/<80 mmHg
- Stage 1: 130-139/80-89 mmHg
- Stage 2: ≥140/≥90 mmHg
- Crisis: >180/>120 mmHg

#### Heart Rate
- Normal rest: 60-100 bpm
- Athletic: 40-60 bpm
- Max: 220 - age

#### Oxygen Saturation
- Normal: 95-100%
- Mild hypoxemia: 90-94%
- Concerning: <90%

---

## Technical Implementation

### Architecture

```
User Query
    ↓
Chatbot Service
    ↓
┌─────────────────────┐
│ 1. Parse message    │
│ 2. Identify topics  │
└─────────────────────┘
    ↓
Web Scraper Service
    ↓
┌─────────────────────────┐
│ 1. Check cache          │
│ 2. Get curated content  │
│ 3. Return knowledge     │
└─────────────────────────┘
    ↓
Chatbot Service
    ↓
┌──────────────────────────┐
│ 1. Personalize response  │
│ 2. Add patient vitals    │
│ 3. Format message        │
└──────────────────────────┘
    ↓
User Response
```

### Caching Strategy

The web scraper implements a simple in-memory cache:

```python
cache_key = f"{topic}_{max_length}"
if cache_key in self.knowledge_cache:
    return self.knowledge_cache[cache_key]
```

This reduces redundant processing for common queries.

### Safety Features

1. **Content Validation**: All health information is pre-vetted
2. **Disclaimer**: Responses remind users to consult healthcare providers
3. **Personalization**: Vitals are incorporated safely
4. **Fallback**: System gracefully handles missing data

---

## Integration with Existing Features

### Patient Context

The chatbot combines web-scraped knowledge with:
- Current vitals (BP, HR, SpO2, steps)
- Patient conditions (from profile)
- Medication information
- Historical trends

### Real-time Updates

Web-enhanced responses update as:
- New vitals are recorded
- Patient conditions change
- Health metrics fluctuate

---

## Future Enhancements

### Planned Features

1. **Live Web Scraping**: Integrate with actual medical websites
   - Mayo Clinic
   - CDC
   - American Heart Association

2. **AI Enhancement**: Use OpenAI with web-scraped context
   ```python
   system_prompt = f"""
   You are a health coach. Use this medical information:
   {web_knowledge}
   
   Patient context: {patient_vitals}
   """
   ```

3. **Multilingual Support**: Translate health knowledge

4. **Citation Tracking**: Provide sources for information

5. **User Feedback**: Learn from user ratings of responses

---

## Testing

### Unit Tests

```python
def test_web_scraper():
    # Test topic scraping
    result = scraper.scrape_health_topic('hypertension')
    assert result is not None
    assert len(result) > 0
    
    # Test health tips
    tips = scraper.search_health_tips('hypertension', 'diet')
    assert len(tips) > 0
    
    # Test normal ranges
    ranges = scraper.get_normal_ranges('blood_pressure')
    assert 'normal' in ranges
```

### Integration Tests

```python
def test_chatbot_with_scraper():
    context = {'latest_vitals': {'blood_pressure': '140/90'}}
    response = chatbot.generate_fallback_response(
        'What about my blood pressure?', 
        context
    )
    assert 'blood pressure' in response.lower()
    assert '140/90' in response
```

---

## Configuration

### Environment Variables

No additional configuration needed. The web scraper works out-of-the-box with curated content.

For future live scraping:
```env
HEALTH_API_KEY=your_api_key
SCRAPING_CACHE_TTL=3600
```

---

## API Documentation

### Complete Endpoint List

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/chat` | POST | Required | Send message to chatbot |
| `/api/chat/history` | GET | Required | Get chat history |
| `/api/chat/suggestions` | GET | Required | Get quick suggestions |
| `/api/health-tips/<id>` | GET | Required | Get health tips |
| `/api/web-knowledge` | GET | Required | Get health knowledge |

### Request/Response Examples

See above sections for detailed examples.

---

## Best Practices

### For Developers

1. **Always cache**: Reduce redundant scraping
2. **Validate sources**: Ensure medical accuracy
3. **Add disclaimers**: Remind users to consult providers
4. **Handle errors**: Graceful fallbacks for failed scraping
5. **Monitor usage**: Track which topics are most requested

### For Content

1. **Cite sources**: Keep track of information origins
2. **Update regularly**: Medical guidelines change
3. **Be specific**: Tailor to chronic conditions
4. **Stay current**: Use latest medical consensus
5. **Personalize**: Incorporate patient data safely

---

## Troubleshooting

### Common Issues

**Issue**: Chatbot returns generic responses
- **Solution**: Check if web scraper is properly initialized

**Issue**: Slow response times
- **Solution**: Verify caching is working, reduce max_length

**Issue**: Outdated information
- **Solution**: Clear cache, update knowledge base

---

## Conclusion

The web scraping integration significantly enhances the chatbot's ability to provide accurate, evidence-based health information while maintaining personalization through patient vitals integration. This creates a more valuable and trustworthy health coaching experience.

---

*Last Updated: 2024*
*Version: 1.0*
