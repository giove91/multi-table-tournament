def context_processor(request):
    return {
        'current_tournament': request.current_tournament,
    }
