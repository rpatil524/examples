package com.vaticle.typedb.example.phoneCalls;

import com.vaticle.typedb.client.TypeDB;
import com.vaticle.typedb.client.api.answer.Numeric;
import com.vaticle.typedb.client.api.connection.TypeDBClient;
import com.vaticle.typedb.client.api.connection.TypeDBSession;
import com.vaticle.typedb.client.api.connection.TypeDBTransaction;
import com.vaticle.typeql.lang.TypeQL;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import javax.xml.stream.XMLStreamException;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.Assert.assertEquals;


public class PhoneCallsTest {

    TypeDBClient client;
    TypeDBSession session;
    String keyspaceName = "phone_calls_java";

    @Before
    public void loadSchema() {
        client = TypeDB.coreClient("localhost:1729");
        client.databases().create(keyspaceName);
        session = client.session(keyspaceName, TypeDBSession.Type.SCHEMA);
        TypeDBTransaction transaction = session.transaction(TypeDBTransaction.Type.WRITE);

        try {
            byte[] encoded = Files.readAllBytes(Paths.get("schemas/phone-calls-schema.gql"));
            String query = new String(encoded, StandardCharsets.UTF_8);
            transaction.query().define(TypeQL.parseQuery(query).asDefine());
            transaction.commit();
            System.out.println("Loaded the " + keyspaceName + " schema");
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            session.close();
        }
        session = client.session(keyspaceName, TypeDBSession.Type.DATA);
    }

    @Test
    public void testCSVMigration() throws FileNotFoundException {
        CSVMigration.main(new String[] { keyspaceName });
        assertMigrationResults();
    }

    @Test
    public void testJSONMigration() throws IOException {
        JSONMigration.main(new String[]{ keyspaceName });
        assertMigrationResults();
    }

    @Test
    public void testXMLMigration() throws FileNotFoundException, XMLStreamException {
        XMLMigration.main(new String[]{ keyspaceName });
        assertMigrationResults();
    }

    @Test
    public void testQueries() throws FileNotFoundException {
        List<Queries.QueryExample> queryExamples = Queries.getTestSubjects();

        Queries.processSelection(0, queryExamples, keyspaceName);

        CSVMigration.main(new String[]{ keyspaceName });

        TypeDBTransaction transaction = session.transaction(TypeDBTransaction.Type.READ);

        ArrayList<String> firstActualAnswer = queryExamples.get(0).executeQuery(transaction);
        Collections.sort(firstActualAnswer);
        ArrayList<String> firstExpectedAnswer = new ArrayList<>(Arrays.asList("+54 398 559 0423", "+370 351 224 5176",
                "+62 107 530 7500", "+81 308 988 7153", "+81 746 154 2598", "+63 815 962 6097", "+7 690 597 4443",
                "+263 498 495 0617"));
        Collections.sort(firstExpectedAnswer);
        assertEquals(firstActualAnswer, firstExpectedAnswer);

        ArrayList<String> secondActualAnswer = queryExamples.get(1).executeQuery(transaction);
        Collections.sort(secondActualAnswer);
        ArrayList<String> secondExpectedAnswer = new ArrayList<>(Arrays.asList("+86 892 682 0628", "+86 202 257 8619",
                "+351 515 605 7915", "+86 922 760 0418", "+63 808 497 1769", "+351 272 414 6570", "+48 894 777 5173",
                "+86 825 153 5518", "+27 117 258 4149", "+1 254 875 4647", "+33 614 339 0298", "+30 419 575 7546"));
        Collections.sort(secondExpectedAnswer);
        assertEquals(secondActualAnswer, secondExpectedAnswer);

        ArrayList<String> thirdActualAnswer = new ArrayList<>(queryExamples.get(2).executeQuery(transaction));
        Collections.sort(thirdActualAnswer);
        ArrayList<String> thirdExpectedAnswer = new ArrayList<>(Arrays.asList("+86 892 682 0628", "+54 398 559 0423"));
        Collections.sort(thirdExpectedAnswer);
        assertEquals(thirdActualAnswer, thirdExpectedAnswer);

        ArrayList<String> forthActualAnswer = new ArrayList<>(queryExamples.get(3).executeQuery(transaction));
        Collections.sort(forthActualAnswer);
        ArrayList<String> forthExpectedAnswer = new ArrayList<>(Arrays.asList("+81 308 988 7153", "+261 860 539 4754",
                "+62 107 530 7500"));
        Collections.sort(forthExpectedAnswer);
        assertEquals(forthActualAnswer, forthExpectedAnswer);

        ArrayList<Numeric> fifthActualAnswer = queryExamples.get(4).executeQuery(transaction);
        ArrayList<Float> fifthExpectedAnswer = new ArrayList<>(Arrays.asList((float) 1242.7715, (float) 1699.4309));
        assertEquals(fifthActualAnswer.size(), fifthExpectedAnswer.size());
        for (int i = 0; i < fifthActualAnswer.size(); i++) {
            assertEquals(fifthActualAnswer.get(i).asDouble(), fifthExpectedAnswer.get(i), 0.0001);
        }

        transaction.close();
    }

    public void assertMigrationResults() {
        TypeDBTransaction transaction = session.transaction(TypeDBTransaction.Type.READ);

        Number numberOfPeople = transaction.query().match(TypeQL.parseQuery("match $x isa person; get $x; count;").asMatchAggregate()).get().asNumber().intValue();
        assertEquals(numberOfPeople, 30);

        Number numberOfCompanies = transaction.query().match(TypeQL.parseQuery("match $x isa company; get $x; count;").asMatchAggregate()).get().asNumber().intValue();
        assertEquals(numberOfCompanies, 1);

        Number numberOfContracts = transaction.query().match(TypeQL.parseQuery("match $x isa contract; get $x; count;").asMatchAggregate()).get().asNumber().intValue();
        assertEquals(numberOfContracts, 10);

        Number numberOfCalls = transaction.query().match(TypeQL.parseQuery("match $x isa call; get $x; count;").asMatchAggregate()).get().asNumber().intValue();
        assertEquals(numberOfCalls, 200);

        transaction.close();
    }

    @After
    public void deleteKeyspace() {
        System.out.println("Deleted the " + keyspaceName + " keyspace");
        client.databases().get(keyspaceName).delete();
        client.close();
    }
}