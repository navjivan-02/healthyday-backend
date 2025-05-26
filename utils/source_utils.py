def parse_source_and_ref(args):
    """
    Extract 'ref' and 'source' from query parameters.
    Returns tuple: (referrer_code, source)
    """
    ref = args.get('ref', '').strip().upper()
    source = args.get('source', '').strip().lower()

    # Default source if not provided
    if not source:
        source = "direct"

    # Clean up empty values
    referrer_code = ref if ref else ""
    return referrer_code, source
