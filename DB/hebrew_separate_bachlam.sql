select q.qtext, a.atext
from questions q	
inner join answers a using (qid)
where q.lang='HE'
and (
atext rlike('[[:<:]]ha[[:>:]]') or
atext rlike('[[:<:]]ba[[:>:]]') or
atext rlike('[[:<:]]ve[[:>:]]') or
atext rlike('[[:<:]]le[[:>:]]') or
atext rlike('[[:<:]]la[[:>:]]') or
atext rlike('[[:<:]]ma[[:>:]]') or
atext rlike('[[:<:]]be[[:>:]]') 
);

select qid, atext
