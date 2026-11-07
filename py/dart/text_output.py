"""Keep native thinking output separate from image-conditioning text."""


class ThinkingBudgetError(ValueError):
    pass


def final_text(output, thinking=False, diagnostics=None):
    text = output.args[0].strip()
    reasoning_present = len(output.args) > 1 and bool(output.args[1].strip())
    if diagnostics is not None:
        diagnostics.update(thinking_requested=bool(thinking), thinking_output_detected=reasoning_present,
                           final_output_present=bool(text))
        if hasattr(output, 'api_usage'):
            diagnostics['api_usage'] = output.api_usage
    if thinking and not text:
        raise ThinkingBudgetError('Thinking mode returned no final answer. The token budget may have been exhausted before the answer. '
                                  'Increase Generation token limit (try 8192–16384), shorten the request, or turn Thinking mode off.')
    return text
