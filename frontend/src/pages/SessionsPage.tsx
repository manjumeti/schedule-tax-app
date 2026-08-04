import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  Alert,
  Box,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useCurrentSession } from "@/context/SessionContext";
import { useDeleteSession, useSaveSession, useSessions } from "@/hooks/useSession";
import { sessionMetadataSchema } from "@/validators/schemas";

interface FormValues {
  name: string;
  assessment_year: string;
}

export function SessionsPage() {
  const { sessionId, setSessionId } = useCurrentSession();
  const { data, isLoading, isError } = useSessions();
  const saveSession = useSaveSession();
  const deleteSession = useDeleteSession();
  const [feedback, setFeedback] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(sessionMetadataSchema),
    defaultValues: { name: "", assessment_year: "2025-26" },
  });

  const onSubmit = (values: FormValues) => {
    saveSession.mutate(
      { name: values.name, assessment_year: values.assessment_year },
      {
        onSuccess: (session) => {
          setSessionId(session.id);
          setFeedback(`Session "${session.name}" created and set as active.`);
          reset({ name: "", assessment_year: values.assessment_year });
        },
      }
    );
  };

  return (
    <Stack spacing={3}>
      <Typography variant="h4">Sessions</Typography>
      <Typography color="text.secondary">
        A session groups your FSI/A3 entries for one assessment year filing. Create one to persist
        entries, view the dashboard, and export reports.
      </Typography>

      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="flex-start">
          <TextField
            label="Session Name"
            {...register("name")}
            error={!!errors.name}
            helperText={errors.name?.message}
          />
          <TextField
            label="Assessment Year"
            placeholder="2025-26"
            {...register("assessment_year")}
            error={!!errors.assessment_year}
            helperText={errors.assessment_year?.message}
          />
          <Button type="submit" variant="contained" disabled={saveSession.isPending}>
            Create Session
          </Button>
        </Stack>
      </form>

      {feedback && <Alert severity="success">{feedback}</Alert>}
      {saveSession.isError && <Alert severity="error">{(saveSession.error as Error).message}</Alert>}

      <Box>
        <Typography variant="h6" gutterBottom>
          Existing Sessions
        </Typography>
        {isLoading && <Typography>Loading...</Typography>}
        {isError && <Alert severity="error">Failed to load sessions</Alert>}
        <List>
          {data?.items.map((session) => (
            <ListItem
              key={session.id}
              secondaryAction={
                <Button color="error" size="small" onClick={() => deleteSession.mutate(session.id)}>
                  Delete
                </Button>
              }
              disablePadding
            >
              <ListItemButton
                selected={session.id === sessionId}
                onClick={() => setSessionId(session.id)}
              >
                <ListItemText
                  primary={`${session.name} (${session.assessment_year})`}
                  secondary={`FSI: ${session.fsi_count} | A3: ${session.a3_count}`}
                />
              </ListItemButton>
            </ListItem>
          ))}
          {data?.items.length === 0 && <Typography color="text.secondary">No sessions yet</Typography>}
        </List>
      </Box>
    </Stack>
  );
}
