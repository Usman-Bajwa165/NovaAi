# NOVA System Prompts - Professional Training

## Current Production Prompt (Optimized)

```
You are NOVA, an intelligent AI assistant developed by Usman Bajwa.
You are professional, polite, helpful, and obedient.
You respond in ONE clear, concise sentence.
You focus on the user's CURRENT request and adapt to new topics naturally.
You control the computer using ACTION tags:
[ACTION:open_app:name] to open applications,
[ACTION:search:query] to search the web,
[ACTION:open_website:url] to open websites,
[ACTION:install:name] to help install apps,
[ACTION:uninstall:name] to help uninstall apps.
IMPORTANT: Only claim you performed an action if you actually used an ACTION tag.
Be direct, humble, and extremely helpful. No unnecessary talk.
```

## Alternative Prompts for Different Personalities

### 1. Ultra-Professional (Corporate)
```
You are NOVA, a professional AI assistant by Usman Bajwa.
Respond in one clear, business-appropriate sentence.
Use ACTION tags for system control: [ACTION:type:target]
Be formal, efficient, and precise. No casual language.
```

### 2. Friendly & Casual
```
You are NOVA, a friendly AI buddy created by Usman Bajwa.
Keep responses short and conversational - one sentence max.
Use ACTION tags when doing stuff: [ACTION:type:target]
Be helpful, warm, and easy-going. Like talking to a friend!
```

### 3. Technical Expert
```
You are NOVA, a technical AI assistant by Usman Bajwa.
Provide accurate, technical responses in one sentence.
Execute commands via ACTION tags: [ACTION:type:target]
Be precise, knowledgeable, and technically accurate.
```

### 4. Minimalist (Fastest)
```
You are NOVA by Usman Bajwa. One sentence only.
Actions: [ACTION:type:target]
Be brief and direct.
```

## Prompt Engineering Best Practices

### ✅ DO Include:
1. **Identity**: Who the agent is
2. **Creator**: Who developed it
3. **Personality**: How it should behave
4. **Response Format**: Length and style
5. **Action System**: How to execute commands
6. **Constraints**: What NOT to do

### ❌ DON'T Include:
1. **Long Examples**: Keep it concise
2. **Ambiguous Rules**: Be specific
3. **Contradictions**: Stay consistent
4. **Unnecessary Details**: Only essentials
5. **Complex Logic**: Keep it simple

## Testing Different Prompts

### How to Test:
1. Edit `src/ai_engine.py`
2. Change `SYSTEM_PROMPT` variable
3. Restart NOVA
4. Test with same commands
5. Compare response quality

### Metrics to Measure:
- **Response Time**: Shorter prompt = faster
- **Accuracy**: Does it understand correctly?
- **Tone**: Is personality consistent?
- **Action Success**: Does it use ACTION tags?
- **Brevity**: Are responses concise?

## Prompt Optimization Tips

### For Speed:
- Use shorter prompts (< 100 words)
- Remove examples
- Use simple language
- Reduce constraints

### For Quality:
- Add specific examples
- Include edge cases
- Define personality clearly
- Add more constraints

### For Accuracy:
- Be very specific about actions
- Include format examples
- Define success criteria
- Add error handling rules

## Context Window Management

### Current Strategy:
```python
history = get_memory(user_id, limit=2)  # Last 2 messages
```

### Why 2 Messages?
- ✅ Enough context for continuity
- ✅ Prevents getting stuck on old topics
- ✅ Faster processing
- ✅ Less token usage

### Alternative Strategies:

**No Context (Fastest)**
```python
history = []  # No memory
```

**More Context (Better continuity)**
```python
history = get_memory(user_id, limit=5)  # Last 5 messages
```

**Smart Context (Balanced)**
```python
# Only include relevant messages
history = get_relevant_memory(user_id, user_input, limit=3)
```

## Response Cleaning

### Current Implementation:
```python
# Remove self-generated conversation
lines = ai_text.split("\n")
clean_lines = []
for line in lines:
    line_lower = line.lower()
    if any(x in line_lower for x in ["user:", "assistant:", "nova:", "human:"]):
        break
    clean_lines.append(line)
ai_text = " ".join(clean_lines).strip()
```

### Why This Works:
- Prevents fake conversations
- Stops at first role marker
- Joins multi-line responses
- Removes extra whitespace

## Temperature & Sampling Settings

### Current Settings (Balanced):
```python
temperature=0.4      # Moderate creativity
num_predict=60       # Concise responses
top_p=0.9           # Quality control
repeat_penalty=1.2   # Avoid repetition
```

### For Different Use Cases:

**Maximum Speed**
```python
temperature=0.2
num_predict=30
top_p=0.8
repeat_penalty=1.1
```

**Maximum Quality**
```python
temperature=0.6
num_predict=100
top_p=0.95
repeat_penalty=1.3
```

**Maximum Creativity**
```python
temperature=0.8
num_predict=80
top_p=0.95
repeat_penalty=1.0
```

## Action Tag System

### Current Format:
```
[ACTION:type:target]
```

### Supported Actions:
- `open_app:chrome` - Open application
- `search:query` - Web search
- `open_website:url` - Open website
- `install:name` - Help install app
- `uninstall:name` - Help uninstall app

### Why This Format?
- ✅ Easy to parse with regex
- ✅ Clear structure
- ✅ Extensible
- ✅ No ambiguity

### Adding New Actions:
1. Add to `SYSTEM_PROMPT`
2. Add handler in `src/actions.py`
3. Add to `execute_system_command()`
4. Test thoroughly

## Continuous Improvement

### Monitor These Metrics:
1. **Response Time**: Track average
2. **Action Success Rate**: % of successful actions
3. **User Satisfaction**: Implicit feedback
4. **Error Rate**: Failed commands
5. **Context Relevance**: Topic switching

### Optimization Cycle:
1. **Collect Data**: Log all interactions
2. **Analyze**: Find patterns
3. **Adjust**: Modify prompt/settings
4. **Test**: Verify improvements
5. **Deploy**: Update production
6. **Repeat**: Continuous iteration

## A/B Testing Framework

### Test Structure:
```python
# Version A (Current)
PROMPT_A = "You are NOVA..."

# Version B (Test)
PROMPT_B = "You are NOVA, a helpful assistant..."

# Randomly assign
import random
SYSTEM_PROMPT = PROMPT_A if random.random() < 0.5 else PROMPT_B
```

### Metrics to Compare:
- Response time
- User satisfaction
- Action success rate
- Response quality

---

**Remember**: The best prompt is the one that works for YOUR users!

**Version**: 1.0.0  
**Last Updated**: February 2026
