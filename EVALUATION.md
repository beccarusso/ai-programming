# Lab 4 Evaluation

Author: Rebecca Russo
Course: CSC 2560 Introduction to AI Development (Agent Lab Part 4)

## 1. Testing prompt

I used an AI assistant (Claude) to generate the tests from the pseudocode specification in the Lab 4 handout. I asked it to work through Lab 4 with me.

> In summary, I asked the AI to review the Lab 4 handout for my Campus Resource Assistant agent as well as the current state of the project, and help me generate the required test code.

## 2. Test code

The tests are in `campus_agent/test_agent.py`. There are five tests, and each one calls `get_campus_resource_info` directly:

| Test | What it checks |
|---|---|
| `test_library_lookup` | "library" returns status "success" and the Library record |
| `test_tutoring_alias` | the alias "tutoring" finds the tutoring record |
| `test_case_insensitive` | "LIBRARY" works the same as "library" |
| `test_resource_not_found` | "dental office" returns status "error" and an error_message containing "Available resources" |
| `test_list_all_resources` | "all" returns an `available_resources` list with at least 4 items |

## 3. What I verified

- All 5 tests pass locally with `python -m pytest test_agent.py -v`.
- The tests also pass with `python test_agent.py` (the plain-Python runner at the bottom of the file).
- The tests run with no `GOOGLE_API_KEY` set, so they do not need an API key, the network or an LLM.
- Before pushing, the tests were run in a fresh Python 3.11 environment with no `.env` file to rehearse what GitHub Actions does.

> I checked the names in the specification (“Library” and “Tutoring Center”) against my data. They did not match, so I had them changed to match.

## 4. What I changed from the specification and why

1. **Expected resource names.** The specification expects the names "Library" and "Tutoring Center". My `campus_resources.json` originally used "Library (Hultquist Library)" and "Learning Center (Tutoring)" (the official JCC names), so tests written exactly from the specification failed against my data. I renamed those two resources in the JSON to "Library" and "Tutoring Center" so the data matches the specification, and I kept the old names as aliases so the official names still work when a student searches for them.
2. **A plain-Python runner.** I added a small `if __name__ == "__main__":` block so the file can also run without pytest, which the handout mentions as an option.

## 5. CI/CD workflow prompt

I used the AI assistant to generate the workflow from the pseudocode specification in the handout.

> I did not write a separate prompt for the workflow. It was generated as part of the same request to work through the Lab 4 handout, using the pseudocode specification for .github/workflows/test.yml in the handout.

## 6. The workflow

The workflow is `.github/workflows/test.yml` at the root of the repository. It runs when code is pushed to `main`, on `ubuntu-latest`, and has four steps:

1. Check out the repository
2. Set up Python 3.11
3. Install dependencies
4. Run the tests with pytest from the `campus_agent` folder

**Result on GitHub:** 
> All three runs passed. In the Actions tab, each run showed a green check mark, and the tests ran in about 30 to 40 seconds. The run for my last commit also passed after I renamed the resources to match the specification.

## 7. What I changed in the workflow and why

1. **Install the project requirements, not only pytest.** The specification says to install pytest. But `agent.py` imports `google-adk` at the top, so on a clean machine the tests would stop with a `ModuleNotFoundError` before any test ran. The workflow installs `campus_agent/requirements.txt` as well as pytest.
2. **Run from the `campus_agent` folder.** The tests import `agent`, so they have to run from that folder (`working-directory: campus_agent`).

## 8. Reflection

**Was the AI-generated code better or worse than what you would write? How?**

> I do believe it was better than what I could write.  AI (in my experience) is very reliable with generating code, specifically, and proves to be a major time saver. I  made sure I checked everything myself after and did a manual review. I also caught the data set mismatch with the required names of Library and Tutoring Center versus the data set. 

**Did you find any "erosion" or "verbosity" (from SlopCodeBench) in the AI's output?**

> The tests are short, and each checks one thing. The only repetition is that every test calls the function and checks the status. I didn’t find any large functions, so I didn’t see erosion. I would still watch for this as the project grows.

**What would you do differently next time you prompt an AI for code?**

> Next time I would give the AI more context before it writes anything, like my actual data file and the files my code imports. The AI wrote tests that expected the names “Library” and “Tutoring Center,” but my data used the official JCC names, so the names didn’t match. It also wrote a workflow that only installed pytest, which would have failed on GitHub because my code needs google-adk. I would also ask for specific quality guidelines, like keeping the code short and not repeating itself, since the SlopCodeBench research says that reduces messy code. And I would always check the result against the requirements before pushing.

**How would you describe the impact this app would have on students at JCC?**

> This app would make it quicker and less stressful for students to find the right office. New students often don’t know whether to go to the Success Center, Financial Aid, or the Library and the answers are spread across different web pages. The assistant gives hours, locations, and contact info in one place at any time of day. It uses information verified against official JCC sources. It says so when it doesn’t know something so students aren’t sent to the wrong place.
