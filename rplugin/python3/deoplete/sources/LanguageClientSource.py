from .base import Base


CompleteOutputs = "g:LanguageClient_omniCompleteResults"


def snippet_neosnippet(candidate):
    import json
    log(json.dumps(candidate, indent=2))
    abbr = candidate.get('abbr')
    snippet = candidate.get('snippet')
    if not abbr or not snippet:
        return None
    neosnippet = {
        'word': abbr,
        'options': {
            'word': 1,
            'onehost': 0,
            'indent': 0,
            'head': 0,
        },
        'snip': snippet + '${0}',
        'user_data': {
            'snippet_trigger': abbr,
            'snippet': snippet + '${0}'
        },
        'real_name': abbr,
        'menu_abbr': snippet
    }

    return neosnippet


def add_snippet_neosnippet(vim, snippet):
    vim.call('neosnippet#helpers#add_snippet', snippet.get('real_name'), snippet)


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = "LanguageClient"
        self.mark = "[LC]"
        self.rank = 1000
        self.min_pattern_length = 1
        self.filetypes = vim.eval(
            "get(g:, 'LanguageClient_serverCommands', {})").keys()
        self.input_pattern += r'(\.|::|->)\w*$'

    def get_complete_position(self, context):
        a = self.vim.call(
            'LanguageClient#get_complete_start', context['input'])
        import json
        log(context['input'])
        return a

    def gather_candidates(self, context):
        if context["is_async"]:
            outputs = self.vim.eval(CompleteOutputs)
            if len(outputs) != 0:
                context["is_async"] = False
                # TODO: error handling.
                candidates = outputs[0].get("result", [])
                for c in candidates:
                    c['word'] = c['abbr']

                # Register snippets.
                # TODO: Delete them later?
                snippets = [s for s in [snippet_neosnippet(c) for c in candidates if c.get('is_snippet')] if s is not None]
                for s in snippets:
                    # Add to snippets here
                    add_snippet_neosnippet(self.vim, s)
                return candidates
        else:
            context["is_async"] = True
            self.vim.command("let {} = []".format(CompleteOutputs))
            character = (context["complete_position"]
                         + len(context["complete_str"]))
            self.vim.funcs.LanguageClient_omniComplete({
                "character": character,
            })
        return []


f = open("/tmp/deoplete.log", "w")


def log(message):
    f.writelines([message])
    f.flush()
