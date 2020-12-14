from asnake.aspace import ASpace


class ArchivesSpaceClient:
    def __init__(self, baseurl, username, password, repository):
        self.client = ASpace(
            baseurl=baseurl,
            username=username,
            password=password,
            repository=repository).client
        self.repository = repository

    def get_diary_refid(self, diary):
        refid = None
        search_url = "repositories/{}/search?page=1&type[]=archival_object&q=digital_object:+{}.pdf".format(
            self.repository, diary)
        results_page = self.client.get(search_url).json()
        if len(results_page.get("results")) == 1:
            refid = results_page.get("results")[0].get("ref_id")
        else:
            raise Exception("{} results found for {}".format(
                len(results_page.get("results")), diary))
        return refid
