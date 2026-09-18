import re

def test_replace():
    tag_mapping = {
        '[FICHA]': '{{ ficha }}',
        '[NOMBRE_EVENTO]': '{{ nombre_evento }}'
    }

    xml_str = "<w:r><w:t>[</w:t></w:r><w:r><w:t>FI</w:t></w:r><w:r><w:t>CHA]</w:t></w:r>"
    
    for simple_tag, jinja_tag in tag_mapping.items():
        pattern_str = ''
        for char in simple_tag:
            if char == '[':
                pattern_str += r'\[(?:<[^>]+>)*'
            elif char == ']':
                pattern_str += r'\]'
            else:
                pattern_str += re.escape(char) + r'(?:<[^>]+>)*'
        
        def repl(match):
            m_str = match.group(0)
            parts = re.split(r'(<[^>]+>)', m_str)
            first_text_idx = -1
            for i in range(0, len(parts), 2):
                if parts[i]:
                    if first_text_idx == -1:
                        first_text_idx = i
                    parts[i] = ""
            if first_text_idx != -1:
                parts[first_text_idx] = jinja_tag
            else:
                parts[0] = jinja_tag
            return "".join(parts)

        xml_str = re.sub(pattern_str, repl, xml_str)

    print("Result:")
    print(xml_str)

test_replace()
