# QC Assist

Tools to support QC of Ford Foundation Grants microfilm digitization

## Installation

- Ensure you have Python 3.11 or later installed on your system: `python --version`
- Install Python requirements using PIP: `pip install -r requirements.txt`
- Install the AWS CLI by following instructions at this URL: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- Update the configuration file located at `config.ini` by adding missing values.


## Configuring AWS credentials

- Configure your AWS SSO credentials following the commands at this URL: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-configure
  - SSO Start URL: https://d-9067b2ab5a.awsapps.com/start/#
  - SSO Region: us-east-1
  - SS0 registration scopes: sso:account:access (default)
  - Use a meaningful profile name (like `rac-sso`)


## Check Package Status

- Log in using the AWS client: `aws sso login --profile rac-sso`
- Move into the directory containing these files: `cd qc_assist`
- Run the script: `python check_package_by_status.py crowley_spreadsheet_path cue_see_csv_path {approved,delivered}`

## Find Data Problems

- Move into the directory containing these files: `cd qc_assist`
- Run the script: `python find_data_problems.py crowley_spreadsheet_path`

## Report Statistics

- Log in using the AWS client: `aws sso login --profile rac-sso`
- Move into the directory containing these files: `cd qc_assist`
- Run the script: `python report.py start_date --end-date (optional)`