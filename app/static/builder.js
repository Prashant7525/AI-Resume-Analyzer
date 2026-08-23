(() => {
    "use strict";

    const STORAGE_KEY = "aiResumeAnalyzer.builder.v4";
    const TEMPLATE_KEY = "resumeBuilderTemplate";

    const MAX_ITEMS = 50;
    const MAX_BULLETS = 20;

    const TEMPLATES = [
        "classic",
        "modern",
        "minimal",
        "executive",
        "developer"
    ];

    const defaultData = {
        name: "",
        email: "",
        phone: "",
        location: "",
        linkedin: "",
        github: "",
        summary: "",
        skills: [],
        experience: [],
        projects: [],
        education: [],
        certifications: [],
        achievements: [],
    };

    const experienceFields = [
        [
            "job_title",
            "Job title",
            "e.g. Software Developer"
        ],
        [
            "company",
            "Company",
            "e.g. Example Technologies"
        ],
        [
            "location",
            "Location",
            "e.g. Bengaluru, India"
        ],
        [
            "start_date",
            "Start date",
            "e.g. Jun 2024"
        ],
        [
            "end_date",
            "End date",
            "e.g. Present"
        ],
    ];

    const projectFields = [
        [
            "name",
            "Project name",
            "e.g. AI Resume Analyzer"
        ],
        [
            "technologies",
            "Technologies",
            "e.g. Python, Flask, SQLite"
        ],
        [
            "url",
            "Project URL",
            "https://..."
        ],
    ];

    const educationFields = [
        [
            "degree",
            "Degree",
            "e.g. B.Tech in Computer Science"
        ],
        [
            "institution",
            "Institution",
            "e.g. ABC University"
        ],
        [
            "location",
            "Location",
            "e.g. Delhi, India"
        ],
        [
            "start_date",
            "Start date",
            "e.g. 2022"
        ],
        [
            "end_date",
            "End date",
            "e.g. 2026"
        ],
        [
            "year",
            "Graduation year",
            "e.g. 2026"
        ],
    ];

    let state = clone(defaultData);
    let saveTimer = null;


    function clone(value) {
        return JSON.parse(
            JSON.stringify(value)
        );
    }


    function cleanString(
        value,
        maxLength = 5000
    ) {
        if (typeof value !== "string") {
            return "";
        }

        return value
            .replace(/\u0000/g, "")
            .replace(/\r\n/g, "\n")
            .replace(/\r/g, "\n")
            .replace(
                /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/g,
                ""
            )
            .trim()
            .slice(
                0,
                maxLength
            );
    }


    function cleanList(
        value,
        maxItems = MAX_ITEMS
    ) {
        if (!Array.isArray(value)) {
            return [];
        }

        return value
            .slice(
                0,
                maxItems
            )
            .map(
                (item) =>
                    cleanString(item)
            )
            .filter(Boolean);
    }


    function normalizeEntry(
        entry,
        fields,
        includeBullets = false
    ) {
        if (
            !entry ||
            typeof entry !== "object" ||
            Array.isArray(entry)
        ) {
            return null;
        }

        const result = {};

        fields.forEach(
            ([key]) => {
                result[key] =
                    cleanString(
                        entry[key]
                    );
            }
        );


        if (
            fields.some(
                ([key]) =>
                    key === "job_title"
            ) &&
            !result.job_title
        ) {
            result.job_title =
                cleanString(
                    entry.role
                );
        }


        if (
            fields.some(
                ([key]) =>
                    key === "name"
            ) &&
            !result.name
        ) {
            result.name =
                cleanString(
                    entry.title
                );
        }


        if (
            fields.some(
                ([key]) =>
                    key === "institution"
            ) &&
            !result.institution
        ) {
            result.institution =
                cleanString(
                    entry.school
                );
        }


        if (includeBullets) {
            result.bullets =
                cleanList(
                    entry.bullets,
                    MAX_BULLETS
                );
        }


        if (
            fields.some(
                ([key]) =>
                    result[key]
            ) ||
            (
                includeBullets &&
                result.bullets.length
            )
        ) {
            return result;
        }

        return null;
    }


    function normalizeState(raw) {
        if (
            !raw ||
            typeof raw !== "object" ||
            Array.isArray(raw)
        ) {
            return clone(
                defaultData
            );
        }

        const next = {
            name:
                cleanString(
                    raw.name
                ),

            email:
                cleanString(
                    raw.email
                ),

            phone:
                cleanString(
                    raw.phone
                ),

            location:
                cleanString(
                    raw.location
                ),

            linkedin:
                cleanString(
                    raw.linkedin
                ),

            github:
                cleanString(
                    raw.github
                ),

            summary:
                cleanString(
                    raw.summary,
                    3000
                ),

            skills:
                cleanList(
                    raw.skills
                ),

            experience: [],

            projects: [],

            education: [],

            certifications:
                cleanList(
                    raw.certifications
                ),

            achievements:
                cleanList(
                    raw.achievements
                ),
        };


        if (
            Array.isArray(
                raw.experience
            )
        ) {
            next.experience =
                raw.experience
                    .slice(
                        0,
                        MAX_ITEMS
                    )
                    .map(
                        (entry) =>
                            normalizeEntry(
                                entry,
                                experienceFields,
                                true
                            )
                    )
                    .filter(Boolean);
        }


        if (
            Array.isArray(
                raw.projects
            )
        ) {
            next.projects =
                raw.projects
                    .slice(
                        0,
                        MAX_ITEMS
                    )
                    .map(
                        (entry) =>
                            normalizeEntry(
                                entry,
                                projectFields,
                                true
                            )
                    )
                    .filter(Boolean);
        }


        if (
            Array.isArray(
                raw.education
            )
        ) {
            next.education =
                raw.education
                    .slice(
                        0,
                        MAX_ITEMS
                    )
                    .map(
                        (entry) =>
                            normalizeEntry(
                                entry,
                                educationFields,
                                false
                            )
                    )
                    .filter(Boolean);
        }


        return next;
    }


    function getElement(id) {
        return document.getElementById(
            id
        );
    }


    function showToast(
        message,
        type = "success"
    ) {
        const toast =
            getElement(
                "builderToast"
            );

        if (!toast) {
            return;
        }

        toast.textContent =
            message;

        toast.className =
            `builder-toast visible ${type}`;

        window.clearTimeout(
            showToast.timer
        );

        showToast.timer =
            window.setTimeout(
                () => {
                    toast.classList.remove(
                        "visible"
                    );
                },
                2200
            );
    }


    function setSaveStatus(
        message
    ) {
        const status =
            getElement(
                "builderSaveStatus"
            );

        if (status) {
            status.textContent =
                message;
        }
    }


    function saveDraft(
        showMessage = false
    ) {
        try {
            localStorage.setItem(
                STORAGE_KEY,
                JSON.stringify(
                    state
                )
            );

            setSaveStatus(
                "Saved locally"
            );

            if (showMessage) {
                showToast(
                    "Draft saved on this device."
                );
            }
        }
        catch (error) {
            setSaveStatus(
                "Local save unavailable"
            );

            if (showMessage) {
                showToast(
                    "Could not save the draft locally.",
                    "error"
                );
            }
        }
    }


    function scheduleSave() {
        setSaveStatus(
            "Saving…"
        );

        window.clearTimeout(
            saveTimer
        );

        saveTimer =
            window.setTimeout(
                () => {
                    saveDraft(false);
                },
                350
            );
    }


    function loadDraft() {
        try {
            const stored =
                localStorage.getItem(
                    STORAGE_KEY
                );

            if (!stored) {
                return false;
            }

            state =
                normalizeState(
                    JSON.parse(
                        stored
                    )
                );

            return true;
        }
        catch (error) {
            localStorage.removeItem(
                STORAGE_KEY
            );

            return false;
        }
    }


    function createField(
        labelText,
        key,
        value,
        placeholder,
        multiline = false
    ) {
        const wrapper =
            document.createElement(
                "div"
            );

        wrapper.className =
            "builder-entry-field";


        const label =
            document.createElement(
                "label"
            );

        label.textContent =
            labelText;

        label.htmlFor =
            `builder-field-${key}-${Math.random()
                .toString(36)
                .slice(2)}`;


        const input =
            multiline
                ? document.createElement(
                    "textarea"
                )
                : document.createElement(
                    "input"
                );


        input.id =
            label.htmlFor;

        input.value =
            value || "";

        input.placeholder =
            placeholder || "";

        input.autocomplete =
            "off";


        wrapper.append(
            label,
            input
        );


        return {
            wrapper,
            input
        };
    }


    function makeEntryCard(
        title,
        fields,
        entry,
        includeBullets,
        index,
        onChange
    ) {
        const card =
            document.createElement(
                "article"
            );

        card.className =
            "builder-entry-card";


        const header =
            document.createElement(
                "div"
            );

        header.className =
            "builder-entry-header";


        const heading =
            document.createElement(
                "h4"
            );

        heading.textContent =
            `${title} ${index + 1}`;


        const remove =
            document.createElement(
                "button"
            );

        remove.type =
            "button";

        remove.className =
            "builder-remove-button";

        remove.textContent =
            "Remove";

        remove.setAttribute(
            "aria-label",
            `Remove ${title.toLowerCase()} ${index + 1}`
        );


        remove.addEventListener(
            "click",
            () => {
                onChange(
                    null,
                    index,
                    true
                );
            }
        );


        header.append(
            heading,
            remove
        );

        card.appendChild(
            header
        );


        const grid =
            document.createElement(
                "div"
            );

        grid.className =
            "builder-entry-grid";


        fields.forEach(
            ([
                key,
                label,
                placeholder
            ]) => {

                const field =
                    createField(
                        label,
                        key,
                        entry[key],
                        placeholder
                    );


                field.input.addEventListener(
                    "input",
                    () => {
                        entry[key] =
                            cleanString(
                                field.input.value
                            );

                        onChange(
                            entry,
                            index,
                            false
                        );
                    }
                );


                grid.appendChild(
                    field.wrapper
                );
            }
        );


        card.appendChild(
            grid
        );


        if (includeBullets) {

            const bullet =
                createField(
                    "Bullet points",
                    `bullets-${index}`,
                    (
                        entry.bullets || []
                    ).join("\n"),
                    "One achievement or responsibility per line",
                    true
                );


            bullet.wrapper.classList.add(
                "builder-entry-full"
            );

            bullet.input.rows =
                4;


            bullet.input.addEventListener(
                "input",
                () => {

                    entry.bullets =
                        cleanList(
                            bullet.input.value.split(
                                "\n"
                            ),
                            MAX_BULLETS
                        );

                    onChange(
                        entry,
                        index,
                        false
                    );
                }
            );


            card.appendChild(
                bullet.wrapper
            );
        }


        return card;
    }


    function renderEntries(
        containerId,
        items,
        config
    ) {
        const container =
            getElement(
                containerId
            );

        if (!container) {
            return;
        }


        container.replaceChildren();


        if (!items.length) {

            const empty =
                document.createElement(
                    "div"
                );

            empty.className =
                "builder-empty-state";

            empty.textContent =
                config.emptyText;

            container.appendChild(
                empty
            );

            return;
        }


        items.forEach(
            (
                entry,
                index
            ) => {

                container.appendChild(
                    makeEntryCard(
                        config.title,
                        config.fields,
                        entry,
                        config.includeBullets,
                        index,
                        (
                            changedEntry,
                            changedIndex,
                            rerender
                        ) => {

                            if (
                                changedEntry ===
                                null
                            ) {
                                items.splice(
                                    changedIndex,
                                    1
                                );
                            }
                            else {
                                items[
                                    changedIndex
                                ] =
                                    changedEntry;
                            }


                            if (rerender) {
                                renderEntries(
                                    containerId,
                                    items,
                                    config
                                );
                            }


                            renderPreview();
                            scheduleSave();
                        }
                    )
                );

            }
        );
    }


    function addEntry(
        section,
        config
    ) {
        if (
            state[
                section
            ].length >=
            MAX_ITEMS
        ) {
            showToast(
                `You can add up to ${MAX_ITEMS} entries.`,
                "error"
            );

            return;
        }


        const entry = {};


        config.fields.forEach(
            ([key]) => {
                entry[key] = "";
            }
        );


        if (
            config.includeBullets
        ) {
            entry.bullets = [];
        }


        state[
            section
        ].push(
            entry
        );


        renderEntries(
            config.containerId,
            state[
                section
            ],
            config
        );


        renderPreview();
        scheduleSave();


        const cards =
            getElement(
                config.containerId
            ).querySelectorAll(
                ".builder-entry-card"
            );


        const last =
            cards[
                cards.length - 1
            ];


        if (last) {

            const firstInput =
                last.querySelector(
                    "input, textarea"
                );

            if (firstInput) {
                firstInput.focus();
            }
        }
    }


    function renderAllEditors() {

        renderEntries(
            "experienceEntries",
            state.experience,
            {
                title: "Experience",

                fields:
                    experienceFields,

                includeBullets: true,

                containerId:
                    "experienceEntries",

                emptyText:
                    "No experience added yet. Add your first role."
            }
        );


        renderEntries(
            "projectEntries",
            state.projects,
            {
                title: "Project",

                fields:
                    projectFields,

                includeBullets: true,

                containerId:
                    "projectEntries",

                emptyText:
                    "No projects added yet. Add a project you want employers to see."
            }
        );


        renderEntries(
            "educationEntries",
            state.education,
            {
                title: "Education",

                fields:
                    educationFields,

                includeBullets: false,

                containerId:
                    "educationEntries",

                emptyText:
                    "No education added yet. Add your latest qualification."
            }
        );
    }


    function syncSimpleFieldsToState() {

        [
            "name",
            "email",
            "phone",
            "location",
            "linkedin",
            "github",
            "summary",
        ].forEach(
            (id) => {

                const input =
                    getElement(id);

                if (input) {

                    state[id] =
                        cleanString(
                            input.value,
                            id === "summary"
                                ? 3000
                                : 5000
                        );
                }
            }
        );


        const skills =
            getElement(
                "skills"
            );


        if (skills) {

            state.skills =
                cleanList(
                    skills.value.split(
                        ","
                    )
                );
        }


        [
            "certifications",
            "achievements"
        ].forEach(
            (id) => {

                const input =
                    getElement(
                        id
                    );

                if (input) {

                    state[id] =
                        cleanList(
                            input.value.split(
                                "\n"
                            )
                        );
                }
            }
        );
    }


    function syncStateToSimpleFields() {

        [
            "name",
            "email",
            "phone",
            "location",
            "linkedin",
            "github",
            "summary",
        ].forEach(
            (id) => {

                const input =
                    getElement(id);

                if (input) {
                    input.value =
                        state[id] || "";
                }
            }
        );


        const skills =
            getElement(
                "skills"
            );


        if (skills) {
            skills.value =
                state.skills.join(
                    ", "
                );
        }


        [
            "certifications",
            "achievements"
        ].forEach(
            (id) => {

                const input =
                    getElement(id);

                if (input) {

                    input.value =
                        state[id].join(
                            "\n"
                        );
                }
            }
        );
    }


    function createPreviewEntryTitle(
        primary,
        secondary
    ) {
        const wrapper =
            document.createElement(
                "div"
            );

        wrapper.className =
            "resume-entry-title";


        const strong =
            document.createElement(
                "strong"
            );

        strong.textContent =
            primary ||
            "Untitled";


        wrapper.appendChild(
            strong
        );


        if (secondary) {

            const span =
                document.createElement(
                    "span"
                );

            span.textContent =
                secondary;

            wrapper.appendChild(
                span
            );
        }


        return wrapper;
    }


    function addText(
        element,
        text,
        className = ""
    ) {
        const p =
            document.createElement(
                "p"
            );

        if (className) {
            p.className =
                className;
        }

        p.textContent =
            text;

        element.appendChild(
            p
        );

        return p;
    }


    function addBullets(
        element,
        bullets
    ) {
        const validBullets =
            cleanList(
                bullets,
                MAX_BULLETS
            );


        if (!validBullets.length) {
            return;
        }


        const ul =
            document.createElement(
                "ul"
            );


        validBullets.forEach(
            (bullet) => {

                const li =
                    document.createElement(
                        "li"
                    );

                li.textContent =
                    bullet;

                ul.appendChild(
                    li
                );
            }
        );


        element.appendChild(
            ul
        );
    }


    function renderContact() {

        const contact =
            getElement(
                "previewContact"
            );


        if (!contact) {
            return;
        }


        contact.replaceChildren();


        const values = [
            [
                "email",
                state.email,
                (value) =>
                    `mailto:${value}`
            ],

            [
                "phone",
                state.phone,
                (value) =>
                    `tel:${value.replace(
                        /\s+/g,
                        ""
                    )}`
            ],

            [
                "location",
                state.location,
                null
            ],

            [
                "linkedin",
                state.linkedin,
                normalizeUrl
            ],

            [
                "github",
                state.github,
                normalizeUrl
            ],
        ];


        values.forEach(
            (
                [
                    key,
                    value,
                    hrefBuilder
                ],
                index
            ) => {

                if (!value) {
                    return;
                }


                if (
                    index > 0 &&
                    contact.childNodes.length
                ) {

                    const separator =
                        document.createElement(
                            "span"
                        );

                    separator.className =
                        "resume-contact-separator";

                    separator.textContent =
                        "·";

                    contact.appendChild(
                        separator
                    );
                }


                if (hrefBuilder) {

                    const link =
                        document.createElement(
                            "a"
                        );

                    link.href =
                        hrefBuilder(
                            value
                        );

                    link.target =
                        key === "email" ||
                        key === "phone"
                            ? "_self"
                            : "_blank";


                    if (
                        key !== "email" &&
                        key !== "phone"
                    ) {

                        link.rel =
                            "noopener noreferrer";
                    }


                    link.textContent =
                        value;


                    contact.appendChild(
                        link
                    );
                }
                else {

                    const span =
                        document.createElement(
                            "span"
                        );

                    span.textContent =
                        value;

                    contact.appendChild(
                        span
                    );
                }
            }
        );


        if (
            !contact.childNodes.length
        ) {
            contact.textContent =
                "Email · Phone · Location";
        }
    }


    function normalizeUrl(
        value
    ) {
        const trimmed =
            cleanString(value);


        if (!trimmed) {
            return "";
        }


        if (
            /^https?:\/\//i.test(
                trimmed
            )
        ) {
            return trimmed;
        }


        return `https://${trimmed}`;
    }


    function setSectionVisible(
        id,
        visible
    ) {
        const section =
            getElement(id);

        if (section) {
            section.hidden =
                !visible;
        }
    }


    function renderPreview() {

        syncSimpleFieldsToState();


        getElement(
            "previewName"
        ).textContent =
            state.name ||
            "Your Name";


        renderContact();


        const summary =
            getElement(
                "previewSummary"
            );


        summary.textContent =
            state.summary ||
            "Your professional summary will appear here.";


        setSectionVisible(
            "previewSummarySection",
            Boolean(
                state.summary
            )
        );


        const skills =
            getElement(
                "previewSkills"
            );


        skills.replaceChildren();


        state.skills.forEach(
            (skill) => {

                const chip =
                    document.createElement(
                        "span"
                    );

                chip.className =
                    "resume-skill";

                chip.textContent =
                    skill;

                skills.appendChild(
                    chip
                );
            }
        );


        setSectionVisible(
            "previewSkillsSection",
            state.skills.length > 0
        );


        renderExperiencePreview();
        renderProjectsPreview();
        renderEducationPreview();


        renderSimpleList(
            "previewCertifications",
            "previewCertificationsSection",
            state.certifications
        );


        renderSimpleList(
            "previewAchievements",
            "previewAchievementsSection",
            state.achievements
        );
    }


    function renderExperiencePreview() {

        const target =
            getElement(
                "previewExperience"
            );


        target.replaceChildren();


        state.experience.forEach(
            (entry) => {

                const item =
                    document.createElement(
                        "article"
                    );

                item.className =
                    "resume-entry";


                const top =
                    document.createElement(
                        "div"
                    );

                top.className =
                    "resume-entry-top";


                top.appendChild(
                    createPreviewEntryTitle(
                        entry.job_title ||
                            "Role",

                        entry.company
                    )
                );


                const meta = [
                    entry.location,

                    entry.start_date &&
                    entry.end_date
                        ? `${entry.start_date} – ${entry.end_date}`
                        : entry.start_date ||
                          entry.end_date
                ]
                    .filter(Boolean)
                    .join(" · ");


                if (meta) {

                    addText(
                        top,
                        meta,
                        "resume-entry-meta"
                    );
                }


                item.appendChild(
                    top
                );


                addBullets(
                    item,
                    entry.bullets
                );


                target.appendChild(
                    item
                );
            }
        );


        setSectionVisible(
            "previewExperienceSection",
            state.experience.length > 0
        );
    }


    function renderProjectsPreview() {

        const target =
            getElement(
                "previewProjects"
            );


        target.replaceChildren();


        state.projects.forEach(
            (entry) => {

                const item =
                    document.createElement(
                        "article"
                    );

                item.className =
                    "resume-entry";


                const top =
                    document.createElement(
                        "div"
                    );

                top.className =
                    "resume-entry-top";


                const title =
                    createPreviewEntryTitle(
                        entry.name ||
                            "Project",

                        entry.technologies
                    );


                if (entry.url) {

                    const link =
                        document.createElement(
                            "a"
                        );

                    link.href =
                        normalizeUrl(
                            entry.url
                        );

                    link.target =
                        "_blank";

                    link.rel =
                        "noopener noreferrer";

                    link.textContent =
                        "View project";

                    link.className =
                        "resume-project-link";

                    title.appendChild(
                        link
                    );
                }


                top.appendChild(
                    title
                );


                item.appendChild(
                    top
                );


                if (entry.description) {

                    addText(
                        item,
                        entry.description
                    );
                }


                addBullets(
                    item,
                    entry.bullets
                );


                target.appendChild(
                    item
                );
            }
        );


        setSectionVisible(
            "previewProjectsSection",
            state.projects.length > 0
        );
    }


    function renderEducationPreview() {

        const target =
            getElement(
                "previewEducation"
            );


        target.replaceChildren();


        state.education.forEach(
            (entry) => {

                const item =
                    document.createElement(
                        "article"
                    );

                item.className =
                    "resume-entry";


                const top =
                    document.createElement(
                        "div"
                    );

                top.className =
                    "resume-entry-top";


                top.appendChild(
                    createPreviewEntryTitle(
                        entry.degree ||
                            "Degree",

                        entry.institution
                    )
                );


                const meta = [
                    entry.location,

                    entry.start_date &&
                    entry.end_date
                        ? `${entry.start_date} – ${entry.end_date}`
                        : entry.year ||
                          entry.start_date ||
                          entry.end_date
                ]
                    .filter(Boolean)
                    .join(" · ");


                if (meta) {

                    addText(
                        top,
                        meta,
                        "resume-entry-meta"
                    );
                }


                item.appendChild(
                    top
                );


                if (entry.details) {

                    addText(
                        item,
                        entry.details
                    );
                }


                target.appendChild(
                    item
                );
            }
        );


        setSectionVisible(
            "previewEducationSection",
            state.education.length > 0
        );
    }


    function renderSimpleList(
        listId,
        sectionId,
        items
    ) {
        const target =
            getElement(
                listId
            );


        target.replaceChildren();


        items.forEach(
            (item) => {

                const li =
                    document.createElement(
                        "li"
                    );

                li.textContent =
                    item;

                target.appendChild(
                    li
                );
            }
        );


        setSectionVisible(
            sectionId,
            items.length > 0
        );
    }


    function clearValidation() {

        document
            .querySelectorAll(
                ".builder-field-error"
            )
            .forEach(
                (element) =>
                    element.remove()
            );


        document
            .querySelectorAll(
                ".invalid"
            )
            .forEach(
                (element) =>
                    element.classList.remove(
                        "invalid"
                    )
            );
    }


    function showFieldError(
        input,
        message
    ) {
        if (!input) {
            return;
        }

        input.classList.add(
            "invalid"
        );


        const error =
            document.createElement(
                "div"
            );

        error.className =
            "builder-field-error";

        error.setAttribute(
            "role",
            "alert"
        );

        error.textContent =
            message;


        input
            .closest(
                ".builder-group, .builder-entry-field"
            )
            ?.appendChild(
                error
            );
    }


    function isValidEmail(
        email
    ) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
            email
        );
    }


    function isValidHttpUrl(
        value
    ) {
        try {
            const url =
                new URL(
                    normalizeUrl(
                        value
                    )
                );

            return (
                url.protocol ===
                    "http:" ||
                url.protocol ===
                    "https:"
            );
        }
        catch {
            return false;
        }
    }


    function validateBuilder() {

        clearValidation();

        let valid = true;


        const name =
            getElement(
                "name"
            );


        const email =
            getElement(
                "email"
            );


        const skills =
            getElement(
                "skills"
            );


        if (!state.name) {

            showFieldError(
                name,
                "Please enter your full name."
            );

            valid = false;
        }


        if (!state.email) {

            showFieldError(
                email,
                "Please enter your email address."
            );

            valid = false;
        }
        else if (
            !isValidEmail(
                state.email
            )
        ) {

            showFieldError(
                email,
                "Please enter a valid email address."
            );

            valid = false;
        }


        if (!state.skills.length) {

            showFieldError(
                skills,
                "Add at least one skill."
            );

            valid = false;
        }


        [
            "linkedin",
            "github"
        ].forEach(
            (id) => {

                const input =
                    getElement(
                        id
                    );


                if (
                    state[id] &&
                    !isValidHttpUrl(
                        state[id]
                    )
                ) {

                    showFieldError(
                        input,
                        "Please enter a valid HTTP or HTTPS URL."
                    );

                    valid = false;
                }
            }
        );


        if (state.phone) {

            const digits =
                state.phone.replace(
                    /\D/g,
                    ""
                );


            if (
                digits.length < 7 ||
                digits.length > 15
            ) {

                showFieldError(
                    getElement(
                        "phone"
                    ),
                    "Please enter a valid phone number."
                );

                valid = false;
            }
        }


        if (
            state.summary.length >
            3000
        ) {

            showFieldError(
                getElement(
                    "summary"
                ),
                "Summary must be 3000 characters or fewer."
            );

            valid = false;
        }


        return valid;
    }


    function fillDemo() {

        state =
            normalizeState(
                {
                    name:
                        "Alex Johnson",

                    email:
                        "alex@example.com",

                    phone:
                        "+91 98765 43210",

                    location:
                        "India",

                    linkedin:
                        "linkedin.com/in/alex",

                    github:
                        "github.com/alex",

                    summary:
                        "Software developer focused on Python, Flask, backend development, and practical application engineering.",

                    skills: [
                        "Python",
                        "Flask",
                        "SQL",
                        "Git",
                        "REST APIs",
                        "JavaScript"
                    ],

                    experience: [
                        {
                            job_title:
                                "Software Developer",

                            company:
                                "Example Company",

                            location:
                                "India",

                            start_date:
                                "2025",

                            end_date:
                                "Present",

                            bullets: [
                                "Developed backend applications using Python and Flask.",

                                "Improved application reliability through automated testing and debugging."
                            ]
                        }
                    ],

                    projects: [
                        {
                            name:
                                "AI Resume Analyzer",

                            technologies:
                                "Python, Flask, SQLite",

                            description:
                                "Built a resume analysis platform with ATS scoring, job matching, analytics, and AI-powered tailoring.",

                            bullets: [
                                "Designed modular analysis services and a responsive dashboard."
                            ],

                            url: ""
                        }
                    ],

                    education: [
                        {
                            degree:
                                "Bachelor of Computer Science",

                            institution:
                                "University",

                            location:
                                "India",

                            start_date:
                                "2022",

                            end_date:
                                "2026",

                            year:
                                "2026",

                            details: ""
                        }
                    ],

                    certifications: [
                        "Python Programming",
                        "Cloud Fundamentals"
                    ],

                    achievements: [
                        "Solved 700+ coding problems.",

                        "Completed a structured problem-solving challenge."
                    ]
                }
            );


        syncStateToSimpleFields();
        renderAllEditors();
        renderPreview();
        saveDraft(false);

        showToast(
            "Demo resume loaded."
        );
    }


    function clearBuilder() {

        if (
            !window.confirm(
                "Clear the current resume? This removes the saved draft on this device."
            )
        ) {
            return;
        }


        state =
            clone(
                defaultData
            );


        localStorage.removeItem(
            STORAGE_KEY
        );


        syncStateToSimpleFields();
        renderAllEditors();
        renderPreview();

        setSaveStatus(
            "Not saved"
        );

        showToast(
            "Resume cleared."
        );
    }


    function exportJson() {

        syncSimpleFieldsToState();


        const blob =
            new Blob(
                [
                    JSON.stringify(
                        state,
                        null,
                        2
                    )
                ],
                {
                    type:
                        "application/json"
                }
            );


        const url =
            URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        const safeName =
            (
                state.name ||
                "resume"
            )
                .replace(
                    /[^a-z0-9]+/gi,
                    "-"
                )
                .replace(
                    /^-+|-+$/g,
                    ""
                )
                .toLowerCase() ||
            "resume";


        link.href =
            url;


        link.download =
            `${safeName}-resume.json`;


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        URL.revokeObjectURL(
            url
        );


        showToast(
            "Resume JSON exported."
        );
    }


    function importJson(
        file
    ) {
        if (!file) {
            return;
        }


        const reader =
            new FileReader();


        reader.onload =
            () => {

                try {

                    state =
                        normalizeState(
                            JSON.parse(
                                reader.result
                            )
                        );


                    syncStateToSimpleFields();
                    renderAllEditors();
                    renderPreview();
                    saveDraft(false);


                    showToast(
                        "Resume imported successfully."
                    );

                }
                catch {

                    showToast(
                        "That file is not a valid resume JSON file.",
                        "error"
                    );
                }
            };


        reader.readAsText(
            file
        );
    }


    function setTemplate(
        template
    ) {

        if (
            !TEMPLATES.includes(
                template
            )
        ) {
            template =
                "classic";
        }


        const preview =
            getElement(
                "resumePreview"
            );


        if (!preview) {
            return;
        }


        TEMPLATES.forEach(
            (name) => {

                preview.classList.remove(
                    `template-${name}`
                );
            }
        );


        preview.classList.add(
            `template-${template}`
        );


        document
            .querySelectorAll(
                ".template-button"
            )
            .forEach(
                (button) => {

                    const active =
                        button.dataset.template ===
                        template;


                    button.classList.toggle(
                        "active",
                        active
                    );


                    button.setAttribute(
                        "aria-pressed",
                        active
                            ? "true"
                            : "false"
                    );
                }
            );


        try {

            localStorage.setItem(
                TEMPLATE_KEY,
                template
            );

        }
        catch {
            // Template preference is optional.
        }
    }


    function setupSimpleFields() {

        [
            "name",
            "email",
            "phone",
            "location",
            "linkedin",
            "github",
            "summary",
            "skills",
            "certifications",
            "achievements",
        ].forEach(
            (id) => {

                const input =
                    getElement(
                        id
                    );


                if (!input) {
                    return;
                }


                input.addEventListener(
                    "input",
                    () => {

                        syncSimpleFieldsToState();
                        clearValidation();
                        renderPreview();
                        scheduleSave();

                    }
                );
            }
        );
    }


    function setupButtons() {

        getElement(
            "addExperience"
        )?.addEventListener(
            "click",
            () =>
                addEntry(
                    "experience",
                    {
                        title:
                            "Experience",

                        fields:
                            experienceFields,

                        includeBullets:
                            true,

                        containerId:
                            "experienceEntries"
                    }
                )
        );


        getElement(
            "addProject"
        )?.addEventListener(
            "click",
            () =>
                addEntry(
                    "projects",
                    {
                        title:
                            "Project",

                        fields:
                            projectFields,

                        includeBullets:
                            true,

                        containerId:
                            "projectEntries"
                    }
                )
        );


        getElement(
            "addEducation"
        )?.addEventListener(
            "click",
            () =>
                addEntry(
                    "education",
                    {
                        title:
                            "Education",

                        fields:
                            educationFields,

                        includeBullets:
                            false,

                        containerId:
                            "educationEntries"
                    }
                )
        );


        getElement(
            "loadDemo"
        )?.addEventListener(
            "click",
            fillDemo
        );


        getElement(
            "clearBuilder"
        )?.addEventListener(
            "click",
            clearBuilder
        );


        getElement(
            "saveBuilder"
        )?.addEventListener(
            "click",
            () => {

                syncSimpleFieldsToState();

                saveDraft(
                    true
                );
            }
        );


        getElement(
            "exportBuilder"
        )?.addEventListener(
            "click",
            exportJson
        );


        getElement(
            "importBuilder"
        )?.addEventListener(
            "click",
            () =>
                getElement(
                    "importFile"
                )?.click()
        );


        getElement(
            "importFile"
        )?.addEventListener(
            "change",
            (event) => {

                importJson(
                    event.target.files?.[0]
                );

                event.target.value =
                    "";
            }
        );


        getElement(
            "printResume"
        )?.addEventListener(
            "click",
            () => {

                syncSimpleFieldsToState();


                if (
                    !validateBuilder()
                ) {

                    showToast(
                        "Please fix the highlighted fields before printing.",
                        "error"
                    );

                    return;
                }


                window.print();
            }
        );


        document
            .querySelectorAll(
                ".template-button"
            )
            .forEach(
                (button) => {

                    button.addEventListener(
                        "click",
                        () =>
                            setTemplate(
                                button.dataset.template
                            )
                    );
                }
            );
    }


    function setupTheme() {

        const toggle =
            getElement(
                "themeToggle"
            );


        const icon =
            getElement(
                "themeIcon"
            );


        if (!toggle) {
            return;
        }


        function updateIcon() {

            const dark =
                document.documentElement
                    .getAttribute(
                        "data-theme"
                    ) === "dark";


            if (icon) {

                icon.textContent =
                    dark
                        ? "🌙"
                        : "☀️";
            }


            toggle.setAttribute(
                "aria-label",
                dark
                    ? "Switch to light mode"
                    : "Switch to dark mode"
            );


            toggle.setAttribute(
                "title",
                dark
                    ? "Switch to light mode"
                    : "Switch to dark mode"
            );
        }


        updateIcon();


        toggle.addEventListener(
            "click",
            () => {

                const dark =
                    document.documentElement
                        .getAttribute(
                            "data-theme"
                        ) === "dark";


                if (dark) {

                    document.documentElement
                        .removeAttribute(
                            "data-theme"
                        );


                    localStorage.setItem(
                        "resume-analyzer-theme",
                        "light"
                    );

                }
                else {

                    document.documentElement
                        .setAttribute(
                            "data-theme",
                            "dark"
                        );


                    localStorage.setItem(
                        "resume-analyzer-theme",
                        "dark"
                    );
                }


                updateIcon();

            }
        );
    }


    function setupBackToTop() {

        const button =
            getElement(
                "backToTop"
            );


        if (!button) {
            return;
        }


        const update =
            () => {

                button.classList.toggle(
                    "visible",
                    window.scrollY >
                        500
                );
            };


        window.addEventListener(
            "scroll",
            update,
            {
                passive: true
            }
        );


        button.addEventListener(
            "click",
            () => {

                window.scrollTo(
                    {
                        top: 0,
                        behavior: "smooth"
                    }
                );
            }
        );


        update();
    }


    function initialize() {

        const initial =
            getElement(
                "builderInitialData"
            );


        let initialData =
            null;


        try {

            initialData =
                initial
                    ? JSON.parse(
                        initial.textContent ||
                        "{}"
                    )
                    : null;

        }
        catch {

            initialData =
                null;
        }


        const params =
            new URLSearchParams(
                window.location.search
            );


        const fromAnalysis =
            params.get(
                "source"
            ) === "analysis";


        const loaded =
            fromAnalysis
                ? false
                : loadDraft();


        if (!loaded) {

            state =
                normalizeState(
                    initialData
                );
        }


        syncStateToSimpleFields();

        renderAllEditors();

        renderPreview();

        setupSimpleFields();

        setupButtons();

        setupTheme();

        setupBackToTop();


        let savedTemplate =
            "classic";


        try {

            savedTemplate =
                localStorage.getItem(
                    TEMPLATE_KEY
                ) || "classic";

        }
        catch {

            // Use default.
        }


        setTemplate(
            savedTemplate
        );


        if (fromAnalysis) {

            saveDraft(
                false
            );

            setSaveStatus(
                "Imported from analysis"
            );

        }
        else if (loaded) {

            setSaveStatus(
                "Saved locally"
            );

        }
        else {

            setSaveStatus(
                "Not saved"
            );
        }
    }


    document.addEventListener(
        "DOMContentLoaded",
        initialize
    );

})();