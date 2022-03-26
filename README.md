# Altana_ai
 
## How to build and run
- Verify python is installed. I am running version 3.7.
- Install the requirements in the provided requirements.txt
- I suggest moving the file `ReceitaFederal_QuadroSocietario.csv` into `/database_utility`, however it is not needed
- Run `build_database.py` from its directory.
    - EG. `cd` into `database_utility` and then run the script
    - Optionally can change input file name using `-f`
        - `python build_database.py -f /docs/file.csv`
    - This should make `database.db` and move it to `/brazilian-api`
- Run the application `/brazilian-api/app.py`
- Hit the endpoints
    - All operators associated with a given company
        - `http://127.0.0.1:5000/operators?company={}`
    - All companies associated with a given operator
        - `http://127.0.0.1:5000/companies?operator={}`
    - All companies connected to a given company via shared operators
        - `http://127.0.0.1:5000/companies?company={}`
    - FYI: Endpoints are limited to 10k responses.
        - `limit` and `offset` are available for you to adjust if needed.

## System Architecture

### API Choices
I chose to go with a REST API. 

##### API Framework
I am choosing to use Flask as the framework for the API. I am choosing to use it for simplicity, and
because it can handle the current task at hand. Albeit, I was tempted to use FastAPI.
- Flask
    - Lightweight. Battle-tested. Easy to get up and running quickly. Handles request synchronously. 
    Perhaps not a good choice for high-load systems.
- Django
    - This is a full stack framework and probably too heavy for this API.
- Tornado
    - This also seems a little too heavy, but could provide asynchronous calls by using non-blocking IO.
- FastAPI
    - It is pretty new. Fast and scalable. Easy to build GraphQL API. Generates documentation for you.
- Falcon
    - Can't serve HTML pages. Not very popular. Fast. Performs at scale. Reliable. Built in SQLAlchemy.

### Project concerns and assumptions

##### My initial concerns/observations
- The data does not really tell me a story. I cannot piece together what the data represents in the real world, or how the
data relates to an event. To me it seems as if each line in an entry would be some sort of event, for instance a business
partner registering for something and this registration is a one time thing, as in once you are registered you don't 
need to register again since you have an ID. Then to me that would explain that a grouping of these items might be unique 
with the exception of a person acting as operator, since the business partner registration ID is masked, otherwise it 
would also hold true. `Company->Business partner registration ID->Operator name` or 
`nm_fantasia->nr_cpf_cpnj_socio->nm_socio` While this holds mostly true, it is not always true. So perhaps registrations 
can occur many times, reusing the same registration id? Either way, this seems to leave me without a unique identifier. 
- The endpoints for the api are not explicitly specified. 
- A response object schema is not specified.
- Performance is not defined to any extent. For instance if this is an API that serves as a large data gathering
tool, I think it would be acceptable for the response to take a couple minutes. However, if this is to be implemented
on a website to allow users to browse data, I do not think anything over a second is acceptable in terms of response time.
- Which, I guess brings up another thing. Who is the consumer? Perhaps we could use something else
to return data. For instance perhaps we could use gPRC instead of a REST API.
- There are no limits defined for amount of data.

#### Assumptions I am making
- The requirements state to use `nm_socio` as a unique key, but it does not appear to be completely unique. Even if I 
pair it with the company ID `nr_cpf_cpnj_socio` it is still not unique. Therefore, I cannot use it as a unique key in
the data model. Therefore, I am taking this to mean when the endpoint to get an operator is hit, this is the attribute 
that will be used and the data model will not use it as a key.
- Due to endpoints not being specified I am making one to return companies and one to return operators. 
- I will return all responses in a similar format for consistency. `{'data': [response_data_0, ..., response_data_n]}`. 
Any error messages will also be return in a similar format.
- I am making the assumption that data should be ready in a reasonable amount of time. Less than a second.
- I am by default allowing the user to only get 10k results, but can be adjusted using `limit` and `offset`

### Data store / model
#### Which store
I am choosing to use SQLite due to simplicity and it will work for this application. Perhaps coupled with my
frustrations when trying to install MySql.
 
With that being said, I did consider other relational databases. I did not consider a document store or NOSQL database
because the data is well structured and a schema can be easily defined.
- SQLite
    - Lightweight. Popular. No configuration. Single file portability. No user management. Limited concurrency. Fast.
Not great with many writes. Server-less.
- MySQL
    - Popular. Fast. Secure users. Replication for scaling. Not great with many writes.
- PostgreSQL
    - Concurrency. Probably too complex for this application. Not as popular, but becoming. Not as fast. Can leverage 
 multiple CPU's.

#### Database schema / model
This was an interesting and hard choice. I am still conflicted with my decision. However, I think provided the required 
output from the application I made a results driven choice. While it is stated I should consider performance, but not
at the expense of design, I feel the performance could make the system unusable.
##### Choice 1
I wanted to make tables based on logical separation of things. For instance I wanted to make a table for all of the
companies and a table for all of the operators. However, via testing this was not a feasible option. I tried optimizing
using many different queries and index solutions, but I could not get a query to execute in a reasonable amount of time.
Even with indexes I could not get a simple join to happen in under 25 seconds. While the more complex join I had was
taking over a minute. I even went as far as making a temporary table to index it to make it even faster. I am deciding
this choice takes too long and is not feasible.
##### Choice 2
I am throwing everything into one table. This keeps me from having to execute joins on the tables. Now with the use of
indexes on the searchable columns I can query the table and join on a CTE in a minimal amount of time. This data easily
goes into one table without really violating anything logically in my opinion and it allows for immeasurable performance
gains when compared to my initial choice.
##### Other decisions
- I suppose it is worth mentioning that I decided to keep the data type as `TEXT` for the numeric(ish) values. Due to the
uncertainty of the meaning behind the leading zeros I feel as if it is best to treat them as unique characters and to
not truncate or ignore them.
- I decided to keep the original field names and use them as the column names in the model. If this model is only used
for this specific data from Brazil, this feels like a good choice or good(ish) at least. I think I would use english
names if this model were to be use more generically.
- I decided to not specify a primary key. This means it will just have the default `rowid` as the unique identifier.
 
## TODO's and/or What next
I am going to run over some things I might have done provided I had some more time to get this done.
- First off, I would add some tests. I am not familiar with testing a Flask application or this probably would have
been the first thing I did. I did create a test csv file to facilitate test driven development, but did not create
actual tests. 
- Seocond, I would add API documentation. I would probably use Swagger to create this documentation.
- I would want to add metrics to this API. The first one that sticks out to me is timing on the queries. This would
allow a  developer to see problematic queries. We could also add metrics for number of times places are queried.
- To build on the previous point, metrics could also point out hot spots. Then caching could be implemented.
- I might add some logging. Although, at this point the built in Flask logging seems sufficient, but perhaps if more
complexity is added to the application logging could be useful.
- I would consider adding versioning to the API.
- Add SSl for security