"""GStudio implementations of osid searches."""

# pylint: disable=too-many-public-methods,too-few-public-methods
#     Number of methods are defined in specification
# pylint: disable=too-many-ancestors
#     Inheritance defined in specification



from .. import utilities
from dlkit.abstract_osid.osid import searches as abc_osid_searches
from ..osid import rules as osid_rules




class OsidSearch(abc_osid_searches.OsidSearch, osid_rules.OsidCondition):
    """``OsidSearch`` specifies search options used to perform OSID searches.

    An ``OsidSearch`` is available from an ``OsidSession`` and defines
    methods to govern the overall search of terms supplied in one or
    more ``OsidQuery`` interfaces.

    This interface is available from a search session.Example using the
    search interface to retrieve the first 25 results:
      OsidSearch os = session.getObjectSearch();
      os.limitResultSet(1, 25);
      
      OsidQuery query;
      query = session.getObjectQuery();
      query.addDescriptionMatch("*food*", wildcardStringMatchType, true);
      
      ObjectSearchResults results = session.getObjectsBySearch(query, os);
      ObjectList list = results.getObjectList();



    """

    @utilities.arguments_not_none
    def limit_result_set(self, start, end):
        """By default, searches return all matching results.

        This method restricts the number of results by setting the start
        and end of the result set, starting from 1. The starting and
        ending results can be used for paging results when a certain
        ordering is requested. The ending position must be greater than
        the starting position.

        arg:    start (cardinal): the start of the result set
        arg:    end (cardinal): the end of the result set
        raise:  InvalidArgument - ``end`` is less than or equal to
                ``start``
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()


class OsidSearchResults(abc_osid_searches.OsidSearchResults, osid_rules.OsidResult):
    """This interface provides a means to capture results of a search.

    An example of searching withina result set: OsidSearch os =
    session.getObjectSearch(); OsidQuery query; query =
    session.getObjectQuery(); query.matchDescription("*food*",
    wildcardStringMatchType, true); ObjectSearchResults results =
    session.getObjectBySearch(query, os); // get information about
    search ObjectList objects = results.getObjects(); int size =
    results.getResultSize(); SearchPerformanceRecord record =
    (SearchPerformanceRecord)
    results.getObjectSearchResultsRecord(performanceRecodType); Duration
    duration = record.getTimeForSearch();

    """

    def get_result_size(self):
        """Returns the size of a result set from a search query.

        This number serves as an estimate to provide feedback for
        refining search queries and may not be the number of elements
        available through an ``OsidList``.

        return: (cardinal) - the result size
        *compliance: mandatory -- This method must be implemented.*

        """
        raise errors.Unimplemented()

    result_size = property(fget=get_result_size)


