# release-ccharp

Handles GitHub flow, user manual export and file copying needed at validation and deployments. 

# Prerequirements
### Installations  (inhouse applications):
* release-tools (https://github.com/Molmed/release-tools)
* confluence-tools (https://github.com/withrocks/confluence-tools)

The GitHub repo of the application must have the branch structure described in https://github.com/Molmed/release-tools.

Input data, e.g. paths, confluence space key, are stored in the release_ccharp.config file.

It have to be .config files in location:
``<root_path>/<repo-name>/buildconfig/release-tools.config``
``<root_path>/<repo-name>/buildconfig/confluence-tools.config``

The rest of the folder structure will be creating when running the workflow the first time.

I have tried to write the code platform independent, although it has only been tested on C# applications. 

Intended workflow:  
``release-ccharp create-cand <repo-name>``  
``release-ccharp download <repo-name>``  
``release-ccharp generate-user-manual <repo-name>`` (optional)  
``release-ccharp accept <repo-name>``  
(write release notes manually at GitHub)  
``release-ccharp download-release-history <repo-name>``  

# Adding a new application 
A new application has to be added to the file release_ccharp.config. It should be self explainatory how to fill it in. 
The changes have to be added to this repo.

# Installation
``pip install -U git+https://github.com/Molmed/release-ccharp.git#egg=release-ccharp``

## Windows
Ensure that you have the python script path ``<python installation dir>/Scripts`` added in your PATH environment variable.

