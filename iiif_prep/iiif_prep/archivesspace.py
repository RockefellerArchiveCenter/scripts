from asnake.aspace import ASpace


class NoResultsError(Exception):
    pass


class MultipleResultsError(Exception):
    pass


class ArchivesSpaceClient:
    def __init__(self, baseurl, username, password, repository):
        self.client = ASpace(
            baseurl=baseurl,
            username=username,
            password=password).client

    def get_diary_refid(self, diary):
        refid = None
        search_url = "repositories/2/search?page=1&type[]=archival_object&q=digital_object:+{}.pdf".format(
            diary)
        results_page = self.client.get(search_url).json()
        if len(results_page.get("results")) == 1:
            refid = results_page.get("results")[0].get("ref_id")
        elif len(results_page.get("results")) == 0:
            raise NoResultsError("0 results found for {}".format(diary))
        elif len(results_page.get("results")) == 2:
            if results_page.get("results")[0].get(
                    "ref_id") == results_page.get("results")[1].get("ref_id"):
                refid = results_page.get("results")[0].get("ref_id")
            else:
                raise MultipleResultsError("{} results found for {}".format(
                    len(results_page.get("results")), diary))
        else:
            raise MultipleResultsError("{} results found for {}".format(
                len(results_page.get("results")), diary))
        return refid
