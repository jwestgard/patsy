# patsy-db

Command-line client for preservation asset tracking system (PATSy)

## Project Branches

This project uses the "GitHub Flow" branching model (see
<https://confluence.umd.edu/display/LIB/GitHub+Flow+Model+for+Kubernetes+configuration+%28k8s-%29+repositories>)

The "main" branch represents version 2 (v2) of the "patsy-db" codebase, which
is incompatible with the "legacy" version 1 (v1) codebase.

Any work on the legacy patsy-db v1 application should be performed on the
"main-v1" branch.

## Development Setup

See [docs/DevelopmentSetup.md](docs/DevelopmentSetup.md).

## Patsy Commands

The "--help" flag provides information about available commands and arguments:

```bash
> patsy --help
```

The "--help" flag, coupled with a specific command shows additional information
about that command:

```bash
> patsy load --help
```

### Common Arguments

## "database" argument

The "--database" argument is used to specify the database the command should
run against.

For SQLite databases, this is typically the filename of the SQLite database
file.

The "--database" argument can be ommited if the user specifies a database to
connect to as an environment variable. The environment variable must be named
"PATSY_DATABASE".

```bash
> export PATSY_DATABASE={database url}
```

The "--database" argument can still be passed in to override the environment
variable temporarily.

If you want to connect to a Postgres database, format the uri as the following:

```bash
postgres+psycopg2://<user>:<password>@address:port/database
```

### "schema" command

Creates the database schema.

```bash
> patsy --database <DATABASE> schema
```

Typically needs only needs to be done once, when the database is created.

### "load" command

Loads an "inventory" CSV file into the database.

```bash
> patsy --database <DATABASE> load <INVENTORY_CSV_FILE>
```

The "inventory" CSV file is typically generated by the "preserve"
(<https://github.com/umd-lib/preserve>) or "aws-archiver"
(<https://github.com/umd-lib/aws-archiver>) tools.

Each row of the CSV file contains information about the batch, accession,
and (optionally) location information about a preservation asset.

An accession is uniquely identified by its batch, and relative path (relpath)
fields. If an accession already exists, the "load" command will NOT update
the accession (even if the accession information in the CSV file is different).
Location information for an existing accession will be added, unless the
location already exists for that accession.

### "checksum" command

Retrieves checksums (MD5 (default), SHA1, or SHA256) for one or more accessions,
looked up by storage location.

```bash
> patsy --database <DATABASE> checksum [--md5|--sha1|--sha256] [LOCATION [LOCATIONS...]]
```

Creates output like this:

```bash
088be3fe9a8fd2a7e70e66a602828766  libdc-archivebucket-17lowbw7m2av1/Archive000Florence/Florence.mpg
fe84e91e0a06906773a5c19a2e9620d9  libdc-archivebucket-17lowbw7m2av1/Archive000Football1/19461130-FB-002-2Qtr.mpg
9876f8c92e16b73c662a39b23409d0a0  libdc-archivebucket-17lowbw7m2av1/Archive000Football1/19461130-FB-003-2Half.mpg
```

Instead of listing locations on the command line, the checksum command
also accepts a CSV file with columns "location" and "destination". If
the "destination" is present, it is used for the second column. Assuming
that the "destination" refers to an actual path on a local file
system, this output can then be fed to `md5sum -c` (or other
algorithm-appropriate checksum verification tool).

```bash
> patsy --database <DATABASE> checksum [--md5|--sha1|--sha256] --file <CSV_FILE>
```

### "sync" command

Store locations of accessions in ApTrust to PATSy.

```bash
> patsy --database <DATABASE> sync --name <API-NAME> --key <API-KEY> [--timebefore|--timeafter] <YEAR-MONTH-DAY>
```

The API-NAME and API-KEY are the X-Pharos-API-User and X-Pharos_API-Key respectively. They are required for the command.
These can be provided in the command or can be added as command-line arguments:

```bash
> export X_PHAROS_KEY=your-email
> export X_PHAROS_KEY=the-secret-key
```

Providing the parameters has more priority than providing them as command-line arguments.

The timebefore and timeafter parameters are dates you can provide to specify what bags to access from ApTrust.
The dates should be formatted in year-month-day format (####-##-##).

## License

See the [LICENSE](LICENSE) file for license rights and limitations.
