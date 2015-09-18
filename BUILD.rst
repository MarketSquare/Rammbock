Rammbock protocol testing library for Robot Framework
=====================================================

Releasing a new version
-----------------------
1. Run the tests.

2. Update the VERSION identifier

    Edit 'src/Rammbock/version.py' in the source repo, commit and push the changes.

3. Create an annotated Git tag in the source repo and push it

    VERSION=N.N git tag -a $VERSION -m "Release $VERSION" && git push --tags

4. Create release on github.

5. Create a source .tar.gz distribution

    python setup.py sdist --formats=gztar

    Verify that the content is correct:

        tar -ztvf dist/robotframework-rammbock-N.N.tar.gz

6. Upload the source distribution to PyPi

    python setup.py sdist register upload

7. Update the docs from gh-pages directory. You can generate the docs with this command:
    
    python gendocs.py

8. Tweet (or re-tweet) about the release as @robotframework to get it into
   News at http://robotframework.org.

9. Send release mails.
