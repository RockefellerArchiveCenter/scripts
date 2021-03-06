from asnake.aspace import ASpace


class NoResultsError(Exception):
    pass


class MultipleResultsError(Exception):
    pass


class ArchivesSpaceClient:
    def __init__(self, baseurl, username, password):
        self.client = ASpace(
            baseurl=baseurl,
            username=username,
            password=password).client

    def get_diary_refid(self, diary):
        refid = None
        search_url = "repositories/2/search?page=1&type[]=archival_object&q=digital_object:+{}.pdf".format(
            diary)
        results_page = self.client.get(search_url).json()
        if results_page.get("total_hits") == 1:
            refid = results_page.get("results")[0].get("ref_id")
        elif results_page.get("total_hits") == 0:
            raise NoResultsError("0 results found for {}".format(diary))
        else:
            if len(list(set([r.get("ref_id") for r in page.get("results")]))) == 1:
                refid = results_page.get("results")[0].get("ref_id")
            else:
                raise MultipleResultsError("{} results found for {}".format(
                    len(results_page.get("results")), diary))
        return refid
