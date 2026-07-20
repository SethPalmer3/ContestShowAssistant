from django.db.models import Sum, Avg, Max, Q
from .models import Event

def get_event_standings(event_id):
    event = Event.objects.get(id=event_id)
    
    standard_filter = Q(scores__is_tie_breaker=False)
    tie_breaker_filter = Q(scores__is_tie_breaker=True)

    if event.score_processor == Event.ScoreProcessor.SUM:
        aggregator = Sum('scores__value', filter=standard_filter)
        tb_aggregator = Sum('scores__value', filter=tie_breaker_filter)
    elif event.score_processor == Event.ScoreProcessor.AVG:
        aggregator = Avg('scores__value', filter=standard_filter)
        tb_aggregator = Avg('scores__value', filter=tie_breaker_filter)
    else:
        aggregator = Max('scores__value', filter=standard_filter)
        tb_aggregator = Max('scores__value', filter=tie_breaker_filter)
        
    results = event.registered_contestants.annotate(
        final_score=aggregator,
        tie_breaker_score=tb_aggregator
    ).filter(final_score__isnull=False)
    
    results_list = list(results)
    reverse_sort = (event.score_order == Event.ScoreOrder.DESC)
    
    def sort_key(contestant):
        score = contestant.final_score if contestant.final_score is not None else 0
        tb_score = contestant.tie_breaker_score if contestant.tie_breaker_score is not None else 0
        return (score, tb_score)

    results_list.sort(key=sort_key, reverse=reverse_sort)

    standings = []
    for i, c in enumerate(results_list):
        rank = i + 1
        is_tied = False
        
        # Round to 2 decimal places to prevent microscopic math errors from breaking ties
        c_score = round(c.final_score, 2) if c.final_score is not None else 0
        c_tb = round(c.tie_breaker_score, 2) if c.tie_breaker_score is not None else 0

        if i > 0:
            prev = standings[-1]
            if c_score == prev['final_score'] and c_tb == prev['tie_breaker_score']:
                rank = prev['actual_rank']
                is_tied = True
                prev['is_tied'] = True 

        standings.append({
            "contestant_name": c.name,
            "show_number": c.show_number,
            "final_score": c_score,
            "tie_breaker_score": c_tb,
            "actual_rank": rank,
            "is_tied": is_tied
        })

    for s in standings:
        s['display_rank'] = f"T-{s['actual_rank']}" if s['is_tied'] else str(s['actual_rank'])

    return standings
